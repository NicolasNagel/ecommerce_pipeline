with calendario as (
    {{
        dbt_utils.date_spine(
            datepart = "day",
            start_date = "cast('2025-01-01' as date)",
            end_date = "cast('2027-12-31' as date)"
        )
    }}
),

enriched as (
    select
        date_day                                        as dt_data,
        extract(year from date_day)::int                as nr_ano,
        extract(quarter from date_day)::int             as nr_trimestre,
        extract(month from date_day)::int               as nr_mes,
        to_char(date_day, 'Month')                      as nm_mes,
        extract(week from date_day)::int                as nr_semana,
        extract(day from date_day)::int                 as nr_dia,
        extract(dow from date_day)::int                 as nr_dia_semana,
        to_char(date_day, 'Day')                        as nm_dia_semana,
        case
            when extract(dow from date_day) in (0, 6) then true
            else false
        end                                             as flg_fim_de_semana,
        concat(
            'T', extract(quarter from date_day)::int,
            '/', extract(year from date_day)::int
        )                                               as nm_trimestre,
        to_char(date_day, 'MM/YYYY')                    as nm_mes_ano
    from calendario
)

select * from enriched