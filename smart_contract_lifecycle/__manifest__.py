{
    'name': 'Smart Contract Lifecycle',
    'version': '19.0.1.1.0',
    'category': 'Sales/CRM',
    'summary': 'Complete lifecycle management for customer and vendor contracts',
    'description': """
Smart Contract Lifecycle
========================
Complete contract management module for Odoo 19.

Features:
---------
* Create and manage customer / vendor contracts
* Contract versioning with full history
* Multi-level approval workflow with amount-based approval matrix
* Automatic alerts: expiry, renewal, milestones
* Financial dashboard: MRR, ARR, renewal rate
* Automatic contract risk score
* Automatic recurring billing (subscriptions)
* Manual signature tracking (with signature image on the PDF)
* Reusable legal clause library
* Professional PDF generation (single contract + list)
* Automatic or manual renewal via wizard
* Contacts, Sales, Purchase, Invoicing integration
* Amendment tracking
* Calendar view of deadlines
* Attachment counter
* Contract templates with dynamic variables
* Partner portal (view + download PDF)
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'price': 59.00,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'contacts',
        'account',
        'sale_management',
        'purchase',
        'product',
        'portal',
    ],
    'data': [
        'security/contract_security.xml',
        'security/ir.model.access.csv',
        'data/contract_sequence.xml',
        'data/contract_mail_templates.xml',
        'data/contract_cron.xml',
        'data/contract_approval_data.xml',
        'data/contract_clause_data.xml',
        'views/contract_views.xml',
        'views/contract_amendment_views.xml',
        'views/contract_template_views.xml',
        'views/contract_dashboard_views.xml',
        'views/contract_approval_views.xml',
        'views/contract_clause_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/portal_contract_views.xml',
        'views/contract_menus.xml',
        'wizard/contract_renew_wizard_views.xml',
        'wizard/contract_send_wizard_views.xml',
        'wizard/contract_clause_insert_wizard_views.xml',
        'report/contract_report.xml',
        'report/contract_report_templates.xml',
    ],
    'demo': [
        'demo/contract_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smart_contract_lifecycle/static/src/css/contract.css',
            'smart_contract_lifecycle/static/src/xml/contract_dashboard.xml',
            'smart_contract_lifecycle/static/src/js/contract_dashboard.js',
        ],
    },
    'images': ['static/src/img/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
