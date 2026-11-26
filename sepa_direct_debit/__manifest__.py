# -*- coding: utf-8 -*-
{
    "name": "SEPA Direct Debit",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Manage SEPA mandates, direct debit batches, and pain.008 file generation with full traceability.",
    "description": """
SEPA Direct Debit
=================
Manage SEPA Direct Debit mandates and collection batches directly in Odoo.

Key features
------------
* SEPA mandate lifecycle: draft, active, suspended, revoked, closed, expired
* IBAN/BIC validation and mandate uniqueness per company
* Mandate signature tracking and bank account history
* Direct debit batches with FRST/RCUR/FNAL/OOFF sequence handling
* pain.008.001.02 XML file generation for bank submission
* Batch controls: totals, line validation, creditor identifier checks
* Chatter tracking on mandates and batches
* Multi-company support and role-based access
""",
    "author": "NORYVEX",
    "website": "https://noryvex.com",
    "support": "imazighenapps@gmail.com",
    "license": "OPL-1",
    "price": 149.0,
    "currency": "EUR",
    "depends": ["account", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ir_cron.xml",
        "views/sdd_mandate_views.xml",
        "views/sdd_batch_views.xml",
        "views/res_partner_views.xml",
        "views/menus.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "images": ["static/description/banner.png"],
    "application": True,
    "installable": True,
}
