with comp as (
    select * from {{ ref('gold_competidores') }}
),

aggregated as (
    select
        id_produto,
        nm_produto,
        cd_categoria,
        vl_preco_atual,
        count(nm_concorrente)                                   as qt_concorrentes,
        round(avg(vl_preco_concorrente)::numeric, 2)            as vl_preco_medio_mercado,
        round(min(vl_preco_concorrente)::numeric, 2)            as vl_preco_minimo_mercado,
        round(max(vl_preco_concorrente)::numeric, 2)            as vl_preco_maximo_mercado,
        round(avg(vl_pct_diferenca)::numeric, 2)                as vl_pct_diferenca_media,
        sum(case when flg_mais_caro then 1 else 0 end)          as qt_concorrentes_mais_baratos,
        case
            when avg(vl_pct_diferenca) > 5  then 'caro'
            when avg(vl_pct_diferenca) < -5 then 'barato'
            else 'competitivo'
        end                                                     as st_posicao_mercado
    from comp
    group by
        id_produto,
        nm_produto,
        cd_categoria,
        vl_preco_atual
)

select * from aggregated