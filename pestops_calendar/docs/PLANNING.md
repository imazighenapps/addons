# PestOps V0.9 — Planning

## Operational flow

Contract -> Treatment Plan -> Visit -> Calendar -> Technician -> Execution

The calendar module is an integration layer over the existing `pest.visit` model. It does not replace PestOps visits with `calendar.event` records.

## Conflict rule

A conflict exists when two visits:
- have the same technician;
- are in draft, scheduled or in-progress state;
- have complete start/end times; and
- overlap in time.

A completed or cancelled visit does not block another visit. A visit without a technician or an end time is not considered a conflict.

## Community-first constraint

The module uses the Community Calendar application and the native calendar view architecture. It does not require Planning, Field Service, Subscriptions or other Enterprise applications.
