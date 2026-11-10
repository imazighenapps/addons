# -*- coding: utf-8 -*-
{
    'name': 'BackorderDesk',
    'version': '19.0.1.0.0',
    'summary': 'Gather every backordered sale line in one queue with the promised date and the message to send to the customer.',
    'description': '''BackorderDesk - Shortages With News
===================================
When a sale cannot ship in full, the shortage hides in delivery notes
and inbox threads. The customer calls for news, the salesperson hunts
for a promised date and the warehouse answers with a different story.
Backorders stay open without an owner, and the message sent to the
customer is rewritten from scratch every time.

BackorderDesk gathers each shortage as a case with the customer,
product, quantity missing, promised date and the latest message to
share. Updates are logged as dated notes so the team can see what was
communicated and when. Resolving a case records the fulfilment date and
moves it out of the open queue, while the open view keeps only what
still needs attention.

* A shortage case per backordered line with customer and product.
* Quantities ordered and missing, plus the promised fulfilment date.
* A customer-facing message kept on the case for quick updates.
* Dated update notes to trace what was communicated and when.
* One open queue showing only unresolved shortages.
* Search filters for late promises and resolved cases.
* Validation that blocks negative quantities and impossible dates.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/backorder_case_0_views.xml',
        'views/backorder_update_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
