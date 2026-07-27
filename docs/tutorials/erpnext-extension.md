# Tutorial: extend ERPNext safely

Declare ERPNext as recommended or required in a NOXUS manifest. Add Custom Fields, hooks, fixtures,
and adapters in the NOXUS app; never edit ERPNext source. Check `frappe.get_installed_apps()` before
resolving an optional link and cover both ERPNext-present and ERPNext-absent paths.
