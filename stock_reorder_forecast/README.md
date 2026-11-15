# ReorderForecast

Consumption-Based Reorder Suggestions

## The problem

SMBs reviewing reorder rules a few times a year either carry excess stock or face stockouts, because rules ignore actual consumption trends.

## The solution

Turn real outgoing consumption into reorder suggestions: average daily issue, stock on hand, incoming quantities and a suggested purchase quantity per product and location.

## Main features

- Consumption lookback window per run.
- Average daily issue from done outgoing moves.
- Suggested quantity net of stock on hand and incoming.
- One open suggestion per product and location, refreshed.
- Ordered, ignored and reopened suggestion states.
- Category filter and location selection.
- Multi-company safe, no Enterprise dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Replenishment** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 18.0 Community and Enterprise.
- Odoo 19.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
