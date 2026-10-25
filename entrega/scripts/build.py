"""Reconstrói tudo a partir dos CSVs, num único comando.

    python entrega/scripts/build.py

Etapas:
1. Confere os CSVs contra o MANIFESTO (SHA-256 e existência dos arquivos).
2. Roda o dbt: deps + build (seeds, modelos e todos os testes). Qualquer teste falho interrompe o build.
3. Exporta os modelos com tag 'published' (só agregados) para Parquet em entrega/dashboard/data/.
4. Gera data_dictionary.json a partir do manifest.json do dbt: é a fonte de documentação do agente.

Variáveis de ambiente opcionais:
    PONTUA_DADOS_DIR       pasta dos CSVs (padrão: contexto/dados)
    PONTUA_MANIFESTO_DIR   pasta do MANIFESTO_v1.csv (padrão: contexto)
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DBT_DIR = REPO / "entrega" / "dbt"
OUT_DIR = REPO / "entrega" / "dashboard" / "data"
DADOS_DIR = Path(os.environ.get("PONTUA_DADOS_DIR", REPO / "contexto" / "dados")).resolve()
MANIFESTO_DIR = Path(os.environ.get("PONTUA_MANIFESTO_DIR", REPO / "contexto")).resolve()
MANIFESTO = MANIFESTO_DIR / "MANIFESTO_v1.csv"


def log(msg: str) -> None:
    print(f"[build] {msg}", flush=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_manifest() -> None:
    log(f"Conferindo CSVs em {DADOS_DIR} contra {MANIFESTO.name}")
    with MANIFESTO.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    problems = []
    for row in rows:
        path = DADOS_DIR / row["arquivo"]
        if not path.exists():
            problems.append(f"{row['arquivo']}: arquivo não encontrado")
            continue
        if sha256(path) != row["sha256"]:
            problems.append(
                f"{row['arquivo']}: SHA-256 diferente do MANIFESTO "
                "(arquivo alterado ou quebras de linha convertidas; ver .gitattributes)"
            )
    if problems:
        for p in problems:
            log(f"ERRO {p}")
        sys.exit(1)
    log(f"{len(rows)} arquivos conferidos (SHA-256 ok). Contagem de linhas é testada no dbt.")


def run_dbt() -> None:
    from dbt.cli.main import dbtRunner

    os.environ.setdefault("PONTUA_DADOS_DIR", DADOS_DIR.as_posix())
    os.environ.setdefault("PONTUA_MANIFESTO_DIR", MANIFESTO_DIR.as_posix())
    os.chdir(DBT_DIR)
    runner = dbtRunner()
    for args in (["deps"], ["build"]):
        log(f"dbt {' '.join(args)}")
        result = runner.invoke([*args, "--profiles-dir", "."])
        if not result.success:
            log(f"ERRO: dbt {args[0]} falhou. Veja o log acima.")
            sys.exit(1)


def published_models(manifest: dict) -> list[dict]:
    return sorted(
        (
            node
            for node in manifest["nodes"].values()
            if node["resource_type"] == "model" and "published" in node.get("tags", [])
        ),
        key=lambda n: n["name"],
    )


def tests_by_column(manifest: dict) -> dict[tuple[str, str | None], list[str]]:
    index: dict[tuple[str, str | None], list[str]] = {}
    for node in manifest["nodes"].values():
        if node["resource_type"] != "test" or not node.get("attached_node"):
            continue
        meta = node.get("test_metadata") or {}
        name = meta.get("name", node["name"])
        index.setdefault((node["attached_node"], node.get("column_name")), []).append(name)
    return index


def export(manifest: dict) -> None:
    import duckdb

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.parquet"):
        old.unlink()

    # Mesma configuração da conexão que o dbt deixa aberta neste processo (read_only diferente é recusado).
    con = duckdb.connect(str(DBT_DIR / "pontua.duckdb"))
    tests = tests_by_column(manifest)
    project_vars = manifest.get("vars", {}) or {}

    dictionary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "dbt manifest.json (descrições e testes de schema.yml) + esquema do DuckDB",
        "how_to_read": (
            "Star schema agregado. Fatos 'agg_*' ligam às dimensões por *_key. "
            "Marts 'mart_*' respondem perguntas específicas da diretoria. "
            "Nenhuma tabela é linha a linha de cliente, conta ou pedido."
        ),
        "project_vars": {k: v for k, v in project_vars.items()},
        "tables": {},
    }

    undocumented_total = []
    for node in published_models(manifest):
        name = node["name"]
        relation = f'{node["schema"]}.{node["alias"]}'
        target = OUT_DIR / f"{name}.parquet"
        raw_schema = con.execute(f"describe {relation}").fetchall()
        # Somas de BIGINT viram HUGEINT no DuckDB; BIGINT é mais portável para Parquet e ferramentas de BI.
        select_list = ", ".join(
            f'cast("{col}" as bigint) as "{col}"' if dtype == "HUGEINT" else f'"{col}"'
            for col, dtype, *_ in raw_schema
        )
        con.execute(f"copy (select {select_list} from {relation}) to '{target.as_posix()}' (format parquet)")
        n_rows = con.execute(f"select count(*) from {relation}").fetchone()[0]
        schema = {col: ("BIGINT" if dtype == "HUGEINT" else dtype) for col, dtype, *_ in raw_schema}

        columns = {}
        for col_name, data_type in schema.items():
            doc = node["columns"].get(col_name, {})
            columns[col_name] = {
                "type": data_type,
                "description": doc.get("description", ""),
                "tests": sorted(tests.get((node["unique_id"], col_name), [])),
                "meta": doc.get("meta") or (doc.get("config") or {}).get("meta") or {},
            }
        undocumented = [c for c, v in columns.items() if not v["description"]]
        undocumented_total += [f"{name}.{c}" for c in undocumented]

        dictionary["tables"][name] = {
            "file": target.name,
            "layer": node["fqn"][2] if len(node["fqn"]) > 2 else "",
            "description": " ".join(node.get("description", "").split()),
            "meta": node.get("meta") or node.get("config", {}).get("meta") or {},
            "rows": n_rows,
            "model_tests": sorted(tests.get((node["unique_id"], None), [])),
            "columns": columns,
            "undocumented_columns": undocumented,
        }
        log(f"exportado {target.name} ({n_rows} linhas)")

    (OUT_DIR / "data_dictionary.json").write_text(
        json.dumps(dictionary, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    log(f"data_dictionary.json com {len(dictionary['tables'])} tabelas")
    con.close()
    # Contrato com o agente e o BI: toda coluna publicada precisa de descrição no schema.yml.
    if undocumented_total:
        log("ERRO: colunas publicadas sem descrição no schema.yml:")
        for c in undocumented_total:
            log(f"  - {c}")
        sys.exit(1)


def main() -> None:
    check_manifest()
    run_dbt()
    manifest = json.loads((DBT_DIR / "target" / "manifest.json").read_text(encoding="utf-8"))
    export(manifest)
    log(f"Pronto. Dados publicados em {OUT_DIR.relative_to(REPO)}")


if __name__ == "__main__":
    main()
