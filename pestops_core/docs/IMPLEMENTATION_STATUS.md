# PestOps Core — implementation status

## Implemented in this iteration

- Recurring visit generation from treatment plans.
- Day/week/month frequencies.
- Generation horizon.
- End-date limiting.
- Idempotent generation strategy based on existing plan visits.
- Scheduled visit creation.
- Default technician propagation.
- Project task creation for operational visits.
- Upcoming-visit reminder activities.
- Treatment product consumption workflow.
- Odoo stock move creation from treatment lines.
- Lot propagation to stock move lines.
- Consumption status on treatment lines and treatment.
- Multi-company propagation.

## Intentionally not implemented yet

- QR scan controller.
- QR print report.
- Service report QWeb.
- Treatment certificate QWeb.
- Mobile technician UI.
- Route optimization.
- Portal.
- Sales integration.
- Accounting integration.
- Advanced scheduling conflicts.
- Stock availability preview before consumption.
- Unit conversion beyond the product's default UoM.
- Automatic treatment suggestions.

## Validation note

The code was syntax-checked and XML-parsed in the build environment.
A real Odoo 19 Community server/database is still required for functional integration testing.
