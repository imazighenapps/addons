# RMA Returns Portal Pro (Odoo 20)

Complete returns management for Odoo 20 Community e-commerce.

## Scope
- Customer self-service portal (/my/returns) with eligibility guards.
- RMA numbering, approval, native reverse pickings, return labels.
- QC grades A/B/C/D mandatory before resolution.
- Refunds via credit notes, exchange orders, store credit, second-life link.

## Install
Copy `rma_returns_portal` into your addons path, update the apps list,
install. Depends on sale, stock, website, portal, account.

## Tests
`odoo -d <db> -i rma_returns_portal --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
