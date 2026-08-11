with awards as (

    select * from {{ ref('stg_awards') }}

),

agencies as (

    select * from {{ ref('stg_agencies') }}

),

recipients as (

    select * from {{ ref('stg_recipients') }}

),

naics as (

    select * from {{ ref('stg_naics') }}

)

select
    awards.award_id,
    recipients.recipient_key,
    agencies.agency_key,
    naics.naics_key,
    awards.start_date,
    awards.end_date,
    awards.award_amount,
    awards.contract_award_type,
    awards.pulled_at
from awards
left join agencies
    on awards.awarding_agency = agencies.awarding_agency
    and awards.awarding_sub_agency = agencies.awarding_sub_agency
left join recipients
    on awards.recipient_name = recipients.recipient_name
left join naics
    on awards.naics_code = naics.naics_code