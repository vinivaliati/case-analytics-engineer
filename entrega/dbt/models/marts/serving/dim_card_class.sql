-- Dimensão publicada. Grão: 1 linha por nível de cartão. PK: card_class_key. Linha '-1' = desconhecido.
-- Nas análises, o nível é o atual do cliente (dim_customer.current_card_class).
with

card_classes as (
    select * from {{ ref('card_classes') }}
)

, final as (
    select
        {{ dbt_utils.generate_surrogate_key(['card_class']) }}  as card_class_key
        , card_class
        , card_class_rank
    from card_classes

    union all

    select
        '-1'                                                    as card_class_key
        , 'Desconhecido'                                        as card_class
        , null                                                  as card_class_rank
)

select * from final
