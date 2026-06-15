with source as (
    select * from {{ source('bronze', 'bronze_preco_competidores') }}
),

renamed as (
    select
        id_produto,
        nome_concorrente                         as nm_concorrente,
        preco_concorrente                        as vl_preco_concorrente,
        data_coleta::timestamp                   as dt_coleta
    from source
)

select * from renamed