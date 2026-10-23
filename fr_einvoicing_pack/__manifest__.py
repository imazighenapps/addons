# -*- coding: utf-8 -*-
{
    "name": "FR E-Invoicing Pack",
    "version": "20.0.1.0.0",
    "summary": "French e-invoicing readiness: Factur-X export, EN16931 validation, e-reporting register, Chorus Pro connector.",
    "description": """
FR E-Invoicing Pack
===================
Professional toolkit for French electronic invoicing obligations (in force
since 1 September 2026 for reception and large companies emission, extended
to SMEs emission on 1 September 2027).

* E-invoicing readiness score for customers and vendors (SIREN/SIRET Luhn,
  VAT, mandatory mentions).
* EN16931 pre-validation blocking non-compliant customer invoices.
* Factur-X (EN16931 profile) XML generation for Odoo Community.
* E-reporting register with CSV export and daily control cron.
* Chorus Pro submission connector (public sector invoices).
* New legal mentions on the invoice report (customer SIREN, delivery
  address, operation type).
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Accounting",
    "license": "OPL-1",
    "price": 89.0,
    "currency": "EUR",
    "depends": ["base", "account"],
    "data": [
        "security/security.xml",
        "security/ir.access.csv",
        "data/system_params.xml",
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
        "views/fr_ereport_views.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
        "report/invoice_report.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
