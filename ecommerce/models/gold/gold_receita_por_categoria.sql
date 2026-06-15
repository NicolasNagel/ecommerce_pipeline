with vendas as (
    select * from {{ ref('silver_vendas') }}
),

produtos as (
    select * from {{ ref('silver_produtos') }}
),

aggregated as (
    select
        p.cd_categoria,
        count(v.id_venda)               as qt_vendas,
        sum(v.qt_itens)                 as qt_itens,
        sum(v.vl_receita)               as vl_receita,
        avg(v.vl_receita)               as vl_ticket_medio,
        sum(v.vl_receita) / sum(sum(v.vl_receita)) over () * 100
                                        as vl_pct_participacao
    from vendas v
    inner join produtos p
        on v.id_produto = p.id_produto
    group by p.cd_categoria
)

select * from aggregated
order by vl_receita desc