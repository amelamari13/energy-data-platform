{{ config(materialized='table') }}

select
    Date(Timestamp) as Date,
    Region,
    AVG(Consumption) as Average_Consumption,
    MAX(Consumption) as Max_Consumption,
    SUM(Total_Production) as Total_Production,
    SUM(Renewable_production) as Renewable_production,
    AVG(Renewable_Share) as Average_Renewable_Share
from {{ ref('stg_energy') }}
group by
    Date,
    Region