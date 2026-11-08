# PrivacyGuard

GDPR Retention and Erasure

## The problem

GDPR forbids keeping personal data forever and forces an answer to every erasure request, but without a dedicated tool nobody knows which records have expired, which fields to mask, or how to prove that a request was handled in time.

## The solution

Set retention periods per model, anonymize sensitive fields, and handle access and erasure requests with dated, auditable proof.

## Main features

- Retention rules per model with date field, days and action.
- Field-by-field anonymization with a configurable mask character.
- Expired data scan with a safe dry run before any change.
- Access, erasure, rectification and portability requests.
- A 30-day legal deadline computed from the request date.
- Status workflow with the user who handled each request.
- Partners are never deleted: erasure masks their personal data.
- Multi-company, traced in the chatter, no Enterprise dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Privacy** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
