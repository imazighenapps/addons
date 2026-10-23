# Employee Referral Bonus (Odoo 19)

Employee referral programme with measurable ROI.

## Scope
- Referral campaigns: bonus on hire, bonus after probation, configurable probation days, currency.
- 4-state referral workflow (submitted → screening → hired → retained) with guards against double-hire and premature retention confirmation.
- Automatic retention due date from the hired employee start date.
- Referrals counted per job and per employee; campaign statistics (hired count, total paid).
- Record rules so employees only see their own referrals.

## Install
Copy `referral_bonus` into your addons path, update the apps list, install.
Depends on base, mail, hr, hr_recruitment.

## Tests
`odoo -d <db> -i referral_bonus --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.