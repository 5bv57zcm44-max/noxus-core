# Tutorial: maintenance SaaS

Run `noxusai new saas --name workshop --industry maintenance --modules inventory,maintenance --yes`.
Set the protected administrator secret and start the development profile. Create an inventory item,
asset, request, technician, and work order; move the order Draft → Scheduled → In Progress → Complete
through `/api/v2/method/noxus_maintenance.api.v1.transition_work_order`.
