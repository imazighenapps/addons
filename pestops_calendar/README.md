# PestOps Calendar — Odoo 19 Community

Community-first operational planning for PestOps visits.

## Features

- Native Odoo Calendar view for `pest.visit`.
- Day/week/month calendar usage through the standard Odoo calendar UI.
- Technician-based event coloring.
- Filters for scheduled visits, today, current week and conflicts.
- Grouping by technician, site and status in list/search contexts.
- Schedule conflict counter on each visit.
- Conflict inspection action from the visit form.
- Prevents scheduling or starting a visit when the same technician has an overlapping active visit with complete start/end times.
- No Odoo Enterprise dependency.

## Dependency model

- `pestops_core`
- Community `calendar`

The module deliberately uses PestOps' existing `scheduled_start` and `scheduled_end` fields rather than introducing a second scheduling model.
