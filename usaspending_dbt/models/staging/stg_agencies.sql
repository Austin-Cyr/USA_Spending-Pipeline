with source as (

    select distinct
        awarding_agency,
        awarding_sub_agency
    from {{ ref('stg_awards') }}
    where awarding_agency is not null

)

select
    {{ dbt_utils.generate_surrogate_key(['awarding_agency', 'awarding_sub_agency']) }} as agency_key,
    awarding_agency,
    awarding_sub_agency
from source