# SEPA Direct Debit

Manage SEPA Direct Debit mandates and collection batches in Odoo.

## Features

- SEPA mandate lifecycle: draft, active, suspended, revoked, expired, closed
- IBAN validation and mandate uniqueness per company
- Mandate signature documents and bank account change history
- Direct debit batches with CORE/B2B schemes and FRST/RCUR/FNAL/OOFF sequence types
- pain.008.001.02 XML generation for bank submission
- Creditor identifier, journal bank account, and line amount validations
- Chatter tracking and multi-company rules

## Configuration

1. Install the module.
2. Assign users to **SEPA Direct Debit / User** or **Manager**.
3. Configure a bank journal with a valid company IBAN.
4. Set your SEPA Creditor Identifier (ICS) on each batch.

## Usage

- Create mandates from **SEPA Direct Debit > Operations > Mandates**.
- Activate mandates after signature verification.
- Create a batch, add collection lines, generate the pain.008 file, and send it to your bank.

## Support

- Author: NORYVEX
- Support: imazighenapps@gmail.com
- License: OPL-1
