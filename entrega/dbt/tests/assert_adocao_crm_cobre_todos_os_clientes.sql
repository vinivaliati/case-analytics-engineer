-- Os segmentos de exposição do mart de CRM somam exatamente a base de clientes (nenhum cliente perdido ou duplicado).
select
    (select sum(customers) from {{ ref('mart_crm_pix_launch_adoption') }})                       as clientes_no_mart
    , (select count(*) from {{ ref('dim_customer') }} where customer_key <> '-1')                as clientes_na_base
where (select sum(customers) from {{ ref('mart_crm_pix_launch_adoption') }})
    <> (select count(*) from {{ ref('dim_customer') }} where customer_key <> '-1')
