with source as (
    select * from {{ source('bronze', 'bronze_clientes') }}
),

renamed as (
    select
        id_cliente,
        nome_cliente        as nm_cliente,
        estado              as sg_estado,
        pais                as nm_pais,
        data_cadastro::timestamp as dt_cadastro
    from source
)

select * from renamed