# HACCP Food Safety Mini (Odoo 18)

Food safety toolkit for small agri-food sites on Odoo 18 Community.

## Scope
- Versioned HACCP plans with team and validation.
- CCPs with min/max/target, units, frequency and method.
- Readings with automatic within/out-of-limits verdict + one-click NC.
- 14 EU allergens pre-loaded, contains/traces on products.
- Expiry alerts cron (DLC/DDM), withdrawal assistant, 5-step NC workflow.

## Install
Copy `haccp_food_safety` into your addons path, update the apps list,
install. Depends on base, mail, product, stock, uom, product_expiry.

## Tests
`odoo -d <db> -i haccp_food_safety --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
