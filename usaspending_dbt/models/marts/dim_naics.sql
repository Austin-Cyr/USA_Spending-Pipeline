select
    naics_key,
    naics_code,
    naics_description
from {{ ref('stg_naics') }}