# QR Pay Pro (Odoo 19)

Premium payment-QR layer on top of native Odoo QR codes (EPC + Swiss).

## Scope
- Automatic RF creditor references (ISO 11649, mod97) with sequences.
- Swiss QRR counter (27 digits, mod10r) with uniqueness per company.
- EPC purpose codes, BIC handling, 331-byte control, payload preview.
- Compliance cockpit (valid/invalid per invoice), camt.053 import wizard,
  EPC payload decoder for vendor bills.

## Install
Copy `qr_pay_pro` into your addons path, update the apps list,
install. Depends on base, account, account_qr_code_sepa.

## Tests
`odoo -d <db> -i qr_pay_pro --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
