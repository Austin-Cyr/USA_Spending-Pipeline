select
    recipient_key,
    recipient_name
from {{ ref('stg_recipients') }}