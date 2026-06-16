with source as (
    select * from {{ source('bronze', 'bronze_vendas') }}
),

renamed as (
    select
        id_venda,
        id_cliente,
        id_produto,
        data_venda::timestamp           as dt_venda,
        canal_venda                     as cd_canal,
        quantidade                      as qt_itens,
        preco_unitario                  as vl_preco_unitario,
        quantidade * preco_unitario     as vl_receita
    from source
)

select * from renamed