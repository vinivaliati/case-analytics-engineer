"""Ferramenta do agente: SQL somente leitura sobre os Parquets publicados (só dados agregados).

Guarda-corpos:
- os Parquets são carregados em memória e o acesso a arquivos/rede é desligado depois disso;
- só aceita um único comando SELECT (ou WITH ... SELECT);
- limita as linhas devolvidas ao modelo;
- interrompe consultas que passarem do tempo limite.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path

import duckdb

from .config import DATA_DIR

MAX_ROWS = 200
TIMEOUT_SECONDS = 10


@dataclass
class QueryResult:
    sql: str
    ok: bool
    columns: list[str] = field(default_factory=list)
    rows: list[list] = field(default_factory=list)
    truncated: bool = False
    error: str | None = None

    def for_model(self) -> dict:
        if not self.ok:
            return {"error": self.error}
        return {
            "columns": self.columns,
            "rows": self.rows,
            "row_count": len(self.rows),
            "truncated": self.truncated,
        }


class SqlTool:
    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.con = duckdb.connect(":memory:")
        self.tables: list[str] = []
        for path in sorted(data_dir.glob("*.parquet")):
            name = path.stem
            self.con.execute(f"create table {name} as select * from read_parquet('{path.as_posix()}')")
            self.tables.append(name)
        # Depois de carregar: sem leitura de arquivos, sem rede, configuração travada.
        self.con.execute("set enable_external_access = false")
        self.con.execute("set lock_configuration = true")

    def _validate(self, sql: str) -> str | None:
        try:
            statements = self.con.extract_statements(sql)
        except duckdb.Error as exc:
            return f"SQL inválido: {exc}"
        if len(statements) != 1:
            return "Envie exatamente um comando SQL."
        if statements[0].type != duckdb.StatementType.SELECT:
            return "Só consultas SELECT são permitidas (somente leitura)."
        return None

    def run(self, sql: str) -> QueryResult:
        sql = sql.strip().rstrip(";")
        problem = self._validate(sql)
        if problem:
            return QueryResult(sql=sql, ok=False, error=problem)

        timer = threading.Timer(TIMEOUT_SECONDS, self.con.interrupt)
        timer.start()
        try:
            cursor = self.con.execute(sql)
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchmany(MAX_ROWS + 1)
        except duckdb.Error as exc:
            return QueryResult(sql=sql, ok=False, error=f"Erro ao executar: {exc}")
        finally:
            timer.cancel()

        truncated = len(rows) > MAX_ROWS
        clean = [[_jsonable(v) for v in row] for row in rows[:MAX_ROWS]]
        return QueryResult(sql=sql, ok=True, columns=columns, rows=clean, truncated=truncated)


def _jsonable(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)
