{
    "name": "FS Configuration Guardian",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Detect, explain and govern Odoo configuration drift",

    "description": """
FS Configuration Guardian helps Odoo administrators and implementation
partners keep production configuration under control.

Core capabilities:
- Create trusted production configuration baselines.
- Capture configuration snapshots using dedicated collectors.
- Compare the current state with a trusted baseline.
- Detect added, modified and removed configuration items.
- Classify configuration changes by risk: Low, Medium, High or Critical.
- Review changes and mark them as Expected, Approved or Rejected.
- Monitor security configuration including users, groups, privileges,
  access controls and record rules.
- Monitor automated actions and scheduled configuration.
- Monitor Studio-related views and custom fields where available.
- Monitor selected accounting, inventory, sales and technical configuration.
- Provide a configuration health score and change counts for each baseline.
- Notify administrators through Odoo chatter and activities when new drift
  is detected.

Product scope:
The module is focused on configuration governance and configuration drift
detection. It is not a generic audit log for every business transaction and
does not automatically modify or repair production configuration.

Security and privacy:
Configuration is collected through the Odoo ORM. Read-only collectors use
elevated read access only to inspect configuration state; collected snapshots
remain inside the Odoo database. No external service is required and no
customer data is sent outside Odoo by this module.

Compatibility:
Designed for Odoo 19 Community and Enterprise. The module uses the Odoo 19
security privilege architecture and Odoo 19 field/view conventions.
""",

    "author": "Farid SLIMANI",
    'website': 'https://slimanifarid.github.io',
    "license": "OPL-1",
    "price": 49.00,
    "currency": "EUR",
    "depends": [
        "base",
        "mail",
    ],

    "data": [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",

        # Data
        "data/guardian_data.xml",

        # Views
        "views/guardian_baseline_views.xml",
        "views/guardian_snapshot_views.xml",
        "views/guardian_change_views.xml",
        "views/guardian_dashboard_views.xml",
        "views/guardian_rule_views.xml",
        "views/guardian_menus.xml",

        # Wizards
        "wizard/guardian_snapshot_wizard_views.xml",
    ],

    "demo": [
        "demo/guardian_demo.xml",
    ],

    "images": [
        "static/images/cover.png",
    ],

    "assets": {
        "web.assets_backend": [
            "fs_configuration_guardian/static/src/js/guardian_dashboard.js",
            "fs_configuration_guardian/static/src/xml/guardian_dashboard.xml",
            "fs_configuration_guardian/static/src/scss/guardian_dashboard.scss",
        ],
    },

    "installable": True,
    "application": True,
    "auto_install": False,
}
