# FuelLog

Vehicle Fuel and Refueling Tracking

## The problem

Fuel spending tracked through generic receipts lacks per-vehicle, per-refueling detail (odometer, liters, cost), making consumption and variance hard to control.

## The solution

Log vehicle refueling with date, odometer, quantity and cost, keep a vehicle catalogue and track fuel spending per vehicle and period in a company-safe register.

## Main features

- Vehicle catalogue with reference/plate and active flag.
- Refueling logs with vehicle, driver, date, odometer, liters and cost.
- Computed price per liter for each entry.
- Draft and confirmed entry states.
- Search and group by vehicle, driver and period.
- Chatter tracking on logs.
- Multi-company safe, no Enterprise dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Fuel Log** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 18.0 Community and Enterprise.
- Odoo 19.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
