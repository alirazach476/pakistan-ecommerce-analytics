-- Business rule: delivery_date >= shipment_date when both present
select shipment_id, shipment_date, delivery_date
from {{ ref('fact_shipments') }}
where delivery_date is not null
  and shipment_date is not null
  and delivery_date < shipment_date
