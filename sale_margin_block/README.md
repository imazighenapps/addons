Sales Margin Block – Odoo 18
===========================

This module prevents the confirmation of Sale Orders if the margin is below
a configurable minimum percentage.

Features
--------
- Automatic margin calculation
- Block confirmation when margin is too low
- Configurable minimum margin
- Manager group can bypass restriction

Configuration
-------------
Settings > Sales > Minimum Margin (%)

Security
--------
Users in group "Allow Low Margin Sales" can confirm orders even if margin is low.
