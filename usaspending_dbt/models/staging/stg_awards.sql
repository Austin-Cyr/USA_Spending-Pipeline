with raw_pages as (

    select
        id as raw_id,
        payload,
        pulled_at
    from {{ source('raw', 'award_responses') }}

),

unnested as (

    select
        raw_id,
        pulled_at,
        jsonb_array_elements(payload -> 'results') as award
    from raw_pages

)

select
    award ->> 'Award ID'              as award_id,
    award ->> 'Recipient Name'        as recipient_name,
    (award ->> 'Start Date')::date    as start_date,
    (award ->> 'End Date')::date      as end_date,
    (award ->> 'Award Amount')::numeric as award_amount,
    award ->> 'Awarding Agency'       as awarding_agency,
    award ->> 'Awarding Sub Agency'   as awarding_sub_agency,
    award ->> 'Contract Award Type'   as contract_award_type,
    award ->> 'NAICS Code'            as naics_code,
    award ->> 'NAICS Description'     as naics_description,
    pulled_at
from unnested