with source as (

    select distinct
        recipient_name
    from {{ ref('stg_awards') }}
    where recipient_name is not null

)

select
    {{ dbt_utils.generate_surrogate_key(['recipient_name']) }} as recipient_key,
    recipient_name
from source