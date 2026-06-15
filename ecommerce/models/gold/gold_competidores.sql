with competitividade as (
    select * from {{ ref('silver_competidores') }}
),

produtos as (
    select * from {{ ref('silver_produtos') }}
),

joined as (
    select
        c.id_produto,
        p.nm_produto,
        p.cd_categoria,
        c.nm_concorrente,
        p.vl_preco_atual,
        c.vl_preco_concorrente,
        p.vl_preco_atual - c.vl_preco_concorrente      as vl_diferenca,
        round(
            ((p.vl_preco_atual - c.vl_preco_concorrente)
            / c.vl_preco_concorrente * 100)::numeric, 2
        )                                               as vl_pct_diferenca,
        case
            when p.vl_preco_atual > c.vl_preco_concorrente then true
            else false
        end                                             as flg_mais_caro,
        case
            when p.vl_preco_atual > c.vl_preco_concorrente then 'acima_mercado'
            when p.vl_preco_atual < c.vl_preco_concorrente then 'abaixo_mercado'
            else 'par_mercado'
        end                                             as st_competitividade,
        c.dt_coleta
    from competitividade c
    inner join produtos p
        on c.id_produto = p.id_produto
)

select * from joined