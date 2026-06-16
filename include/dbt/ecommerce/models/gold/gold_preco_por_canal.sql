with vendas as (
    select * from {{ ref('silver_vendas') }}
),

aggregated as (
    select
        cd_canal,
        dt_venda::date                  as dt_venda,
        count(id_venda)                 as qt_vendas,
        sum(qt_itens)                   as qt_itens,
        sum(vl_receita)                 as vl_receita,
        avg(vl_receita)                 as vl_ticket_medio
    from vendas
    group by cd_canal, dt_venda::date
)

select * from aggregated