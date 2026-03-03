# -*- coding: utf-8 -*-
{
    'name': 'Smart Follow-up Reminder',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Automatic reminders on unanswered quotes, 1-click notifications',
    'description': """
Smart Follow-up Reminder
========================
Automate your sales follow-up process with intelligent reminders on unanswered
quotations. Configure follow-up delays per sales team, send reminders with
1-click, and escalate overdue quotes to managers automatically.

Key Features:
- Automatic daily cron to detect unanswered quotes
- Configurable delays per sales team (1st, 2nd reminder, escalation)
- 1-click follow-up wizard with pre-filled email template
- Follow-up status badge on quotation list and form views
- Kanban board of quotes to follow up
- Manager escalation with Odoo activity notifications
- Minimum amount threshold to avoid reminders on small quotes
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'mail', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'views/followup_config_views.xml',
        'views/sale_order_views.xml',
        'views/followup_wizard_views.xml',
        'views/followup_kanban_views.xml',
        'views/menus.xml',
    ],
    'images': ['static/description/img.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 30.0,
    'currency': 'EUR',
}
