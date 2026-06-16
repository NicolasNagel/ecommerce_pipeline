with clientes as (
    select * from {{ ref('silver_clientes') }}
),

vendas as (
    select * from {{ ref('silver_vendas') }}
),

aggregated as (
    select
        c.id_cliente,
        c.nm_cliente,
        c.sg_estado,
        c.nm_pais,
        c.dt_cadastro,
        count(v.id_venda)           as qt_pedidos,
        sum(v.vl_receita)           as vl_receita_total,
        avg(v.vl_receita)           as vl_ticket_medio,
        min(v.dt_venda)             as dt_primeira_compra,
        max(v.dt_venda)             as dt_ultima_compra,
        max(v.dt_venda) - min(v.dt_venda)   as nr_dias_relacionamento
    from clientes c
    left join vendas v
        on c.id_cliente = v.id_cliente
    group by
        c.id_cliente,
        c.nm_cliente,
        c.sg_estado,
        c.nm_pais,
        c.dt_cadastro
)

select * from aggregated