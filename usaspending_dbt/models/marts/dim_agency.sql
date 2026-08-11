select
    agency_key,
    awarding_agency,
    awarding_sub_agency
from {{ ref('stg_agencies') }}