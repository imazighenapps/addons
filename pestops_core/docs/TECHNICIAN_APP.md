# PestOps Technician Workspace — V0.4

The technician app is a backend client action built with Owl.

## Main workflow

Today's visits
-> Open visit
-> Start
-> Inspect point / Inspect all
-> Capture photos
-> Save inspection
-> Create treatment
-> Select product + lot + quantity
-> Save treatment
-> Consume products
-> Finish visit

## Design rule

This app is a mobile-first operational layer. It does not replace normal Odoo form views.

The backend forms remain available for supervisors/managers.

## Community compatibility

The UI uses Odoo's web/Owl framework and the Community models:
- pest.visit
- pest.inspection
- pest.inspection.line
- pest.treatment
- pest.treatment.line
- product.product
- stock.lot
- stock.location

No Enterprise module is required.

## Validation

The build environment validates JavaScript as text-level module code only by packaging it; a real Odoo 19 browser session is still required to validate Owl rendering and RPC calls.
