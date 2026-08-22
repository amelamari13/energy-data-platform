select
    Timestamp,
    Region,
    Consumption,
    Thermal,
    Nuclear,
    Wind,
    Solar,
    Hydro,
    Bioenergy,
    Total_Production,
    Renewable_production,
    Renewable_Share
from {{ source('energy', 'clean_energy') }}