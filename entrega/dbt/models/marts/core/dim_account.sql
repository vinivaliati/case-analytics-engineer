-- Grão: 1 linha por conta de cartão. PK: account_key. Linha '-1' = conta desconhecida.
with

cards as (
    select * from {{ ref('stg_cartoes__cards') }}
)

, card_classes as (
    select * from {{ ref('card_classes') }}
)

, accounts as (
    select
        {{ dbt_utils.generate_surrogate_key(['cards.account_id']) }}    as account_key
        , cards.account_id
        , {{ dbt_utils.generate_surrogate_key(['cards.user_id']) }}     as customer_key
        , cards.user_id
        , cards.card_class
        , card_classes.card_class_rank
        , cards.card_brand
        , cards.card_created_at
        , cards.is_most_recent
    from cards
    left join card_classes
        on cards.card_class = card_classes.card_class
)

, unknown_member as (
    select
        '-1'                                as account_key
        , null                              as account_id
        , '-1'                              as customer_key
        , null                              as user_id
        , 'Desconhecido'                    as card_class
        , null                              as card_class_rank
        , 'Desconhecido'                    as card_brand
        , null                              as card_created_at
        , null                              as is_most_recent
)

select * from accounts
union all
select * from unknown_member
