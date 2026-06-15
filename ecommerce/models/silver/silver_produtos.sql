with source as (
    select * from {{ source('bronze', 'bronze_produtos') }}
),

renamed as (
    select
        id_produto,
        nome_produto        as nm_produto,
        categoria           as cd_categoria,
        marca               as nm_marca,
        preco_atual         as vl_preco_atual,
        data_criacao::timestamp as dt_criacao
    from source
)

select * from renamed