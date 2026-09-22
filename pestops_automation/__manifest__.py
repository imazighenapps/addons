{
    'name': 'PestOps Notifications & Automations',
    'version': '18.0.1.3.1',
    'category': 'Services',
    'summary': 'Proactive reminders, escalations and customer notifications for PestOps',
    'description': '''
PestOps Notifications & Automations adds configurable proactive workflows:
visit reminders, overdue visits, contract renewal alerts, overdue anomalies,
customer notifications for service requests and published portal documents,
and a traceable automation event log.

Designed for Odoo Community 19.0.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'pestops_stock',
        'pestops_portal',
        'mail',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron.xml',
        'views/automation_config_views.xml',
        'views/automation_log_views.xml',
        'views/pestops_automation_menus.xml',
    ],
    'application': False,
    'installable': True,
}
