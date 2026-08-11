with source as (

    select distinct
        naics_code,
        naics_description
    from {{ ref('stg_awards') }}
    where naics_code is not null

)
Select
    {{ dbt_utils.generate_surrogate_key(['naics_code']) }} as naics_key,
    naics_code,
    naics_description
from source