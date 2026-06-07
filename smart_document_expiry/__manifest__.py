# -*- coding: utf-8 -*-
{
    'name': 'Smart Document Expiry Tracker',
    'version': '18.0.2.1.0',
    'category': 'Documents',
    'summary': 'Track expiry dates for persons, vendors, vehicles & equipment — fully standalone.',
    'description': """
Smart Document Expiry Tracker
==============================
Automatically track and manage expiring documents across your entire organization.
100% standalone — no dependency on hr, fleet, stock, portal or maintenance modules.

Features:
---------
* Universal document management — persons, vendors, vehicles, equipment, or any custom entity
* Configurable email alerts at 90, 30, and 7 days before expiry
* Color-coded Kanban & List dashboard (Green / Orange / Red)
* Escalation alerts if document is not renewed after deadline
* Compliance score per entity
* Full renewal history and archiving
* Exportable PDF compliance reports
* Odoo main dashboard widget
* Configurable document type categories

Ideal for:
----------
HR departments, Fleet managers, Procurement teams, HSE officers
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'price': 34.99,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        # Security
        'security/document_expiry_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/document_type_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',

        # Views — entities
        'views/document_person_views.xml',
        'views/document_partner_views.xml',
        'views/document_vehicle_views.xml',
        'views/stock_equipment_views.xml',

        # Views — core
        'views/document_expiry_views.xml',
        'views/document_type_views.xml',
        'views/document_dashboard_views.xml',

        # Wizards
        'wizards/document_renew_wizard_views.xml',

        'views/menu_views.xml',

        # Reports
        'report/document_expiry_report.xml',
        'report/document_expiry_report_templates.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smart_document_expiry/static/src/css/document_expiry.css',
            'smart_document_expiry/static/src/xml/document_expiry_dashboard.xml',
            'smart_document_expiry/static/src/js/document_expiry_widget.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
