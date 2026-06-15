with vendas as (
    select * from {{ ref('silver_vendas') }}
),

produtos as (
    select * from {{ ref('silver_produtos') }}
),

aggregated as (
    select
        v.id_produto,
        p.nm_produto,
        p.cd_categoria,
        p.nm_marca,
        p.vl_preco_atual,
        count(v.id_venda)               as qt_vendas,
        sum(v.qt_itens)                 as qt_itens,
        sum(v.vl_receita)               as vl_receita,
        avg(v.vl_preco_unitario)        as vl_ticket_medio,
        rank() over (
            order by sum(v.vl_receita) desc
        )                               as nr_rank_receita
    from vendas v
    inner join produtos p
        on v.id_produto = p.id_produto
    group by
        v.id_produto,
        p.nm_produto,
        p.cd_categoria,
        p.nm_marca,
        p.vl_preco_atual
)

select * from aggregated