# Review Booster (Odoo 20)

Collect Google reviews automatically, with a real opt-in proof trail.

## Scope
- Review campaigns with a Google review URL, a trigger (invoice posting or
  delivery) and a send delay.
- Per-customer opt-in flag plus an opt-in proof text (GDPR-friendly: no request
  is ever sent without consent).
- Review requests generated once per invoice or delivery, never duplicated.
- Short redirect link `/r/<token>` that records the click and forwards to
  Google, so engagement is measurable.
- Opt-out that writes back to the customer record and stops future requests.
- Daily cron sending the due requests through a mail template.

## Install
Copy `review_booster` into your addons path, update the apps list, install.
Depends on base, mail, account, stock, website.

## Tests
`odoo -d <db> -i review_booster --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.