# PestOps Contract Engine — V0.5

The Community core now supports a dedicated PestOps contract model.

## Workflow

Customer
-> Contract
-> Contract Sites
-> Confirm
-> Treatment Plans
-> Recurring Visits
-> Field/Project Tasks
-> Operations

## Contract design

A contract can cover multiple customer sites.

Each contract site can override:
- Frequency
- Visit duration
- Technician
- Visit generation horizon

The contract header provides defaults.

## Statuses

Draft
Confirmed
Suspended
To Renew
Expired
Cancelled

## Important product decision

The Community core stores amount and billing frequency as business information.
It does NOT require Accounting or Sales.

Those integrations should be separate modules:
- pestops_sale
- pestops_account

This keeps PestOps Core Community-only.

## Renewal automation

A daily cron:
- expires confirmed contracts after their end date;
- disables their plans;
- moves contracts to "To Renew" when the end date is within 30 days.

## Plan generation

Confirming a contract creates or updates one treatment plan per contract site.
The existing recurring visit engine then generates visits from these plans.
