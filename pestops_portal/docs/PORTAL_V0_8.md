# PestOps Portal V0.8

## Added
- Portal document center at `/my/pestops/documents`.
- Secure customer-scoped document download route.
- `pest.portal.document` model for explicit portal publication.
- Backend actions to generate and publish service reports and treatment certificates.
- Dashboard document KPI and recent documents table.
- Documents remain linked to customer/site/visit/treatment for traceability.

## Community compatibility
No Enterprise module is required. The feature relies on `portal`, `mail`, `ir.attachment` and PestOps Community models.

## Security rule
Portal download always checks the published flag and commercial partner ownership before returning the attachment bytes.

## Validation note
The package is syntax/XML/CSV validated in the build environment. It should still be installed in a real Odoo 19 Community database for final integration testing.
