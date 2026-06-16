with produtos as (
    select * from {{ ref('silver_produtos') }}
),

competitividade as (
    select * from {{ ref('gold_competidores') }}
),

joined as (
    select
        p.id_produto,
        p.nm_produto,
        p.cd_categoria,
        p.nm_marca,
        p.vl_preco_atual,
        p.dt_criacao,
        c.qt_concorrentes,
        c.vl_preco_medio_mercado,
        c.vl_preco_minimo_mercado,
        c.vl_preco_maximo_mercado,
        c.vl_pct_diferenca_media,
        c.qt_concorrentes_mais_baratos,
        c.st_posicao_mercado
    from produtos p
    left join competitividade c
        on p.id_produto = c.id_produto
)

select * from joined