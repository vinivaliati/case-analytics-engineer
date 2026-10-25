-- Grão: 1 linha por cliente (user_id). PK: customer_key. Linha '-1' = cliente desconhecido.
-- current_card_class = nível da conta marcada como is_most_recent (exatamente 1 por cliente na v1).
with

cards as (
    select * from {{ ref('stg_cartoes__cards') }}
)

, card_classes as (
    select * from {{ ref('card_classes') }}
)

, per_customer as (
    select
        user_id
        , count(*)                          as accounts_count
        , min(card_created_at)              as first_card_created_at
        , max(card_created_at)              as last_card_created_at
    from cards
    group by user_id
)

, current_account as (
    select
        user_id
        , account_id                        as current_account_id
        , card_class                        as current_card_class
        , card_brand                        as current_card_brand
    from cards
    where is_most_recent
)

, customers as (
    select
        {{ dbt_utils.generate_surrogate_key(['per_customer.user_id']) }} as customer_key
        , per_customer.user_id
        , current_account.current_account_id
        , current_account.current_card_class
        , card_classes.card_class_rank      as current_card_class_rank
        , current_account.current_card_brand
        , per_customer.accounts_count
        , per_customer.first_card_created_at
        , per_customer.last_card_created_at
    from per_customer
    left join current_account
        on per_customer.user_id = current_account.user_id
    left join card_classes
        on current_account.current_card_class = card_classes.card_class
)

, unknown_member as (
    select
        '-1'                                as customer_key
        , null                              as user_id
        , null                              as current_account_id
        , 'Desconhecido'                    as current_card_class
        , null                              as current_card_class_rank
        , 'Desconhecido'                    as current_card_brand
        , null                              as accounts_count
        , null                              as first_card_created_at
        , null                              as last_card_created_at
)

select * from customers
union all
select * from unknown_member
