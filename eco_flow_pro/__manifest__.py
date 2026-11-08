# -*- coding: utf-8 -*-
{
    'name': 'EcoFlowPro',
    'version': '19.0.1.0.0',
    'summary': 'Turn every bill of materials correction into a tracked engineering change request with review, approval and one-click application on the BOM.',
    'description': '''EcoFlowPro - Engineering Change Orders on Bills of Materials
============================================================
Before mass production, engineering teams adjust bills of materials all
the time: a quantity is corrected after a first trial run, a part is
added following a supplier recommendation, or a component is dropped
after a cost review. In plain Odoo these corrections are made directly
on the BOM, so nobody can tell who requested the change, why it was
needed, or on which date it takes effect. Worse, the BOM of a running
product can be modified by mistake while a version is still being
validated by the quality or production team. EcoFlowPro turns every
correction into a formal engineering change request with its own ECO
number, requester, approver and effective date. Each request lists its
lines by component with a change type - add, remove or change - plus the
old and the new quantity. The request follows a simple workflow: draft,
review, approved, applied or refused, and every step is traced in the
chatter. When the approver applies the change, Odoo updates the
referenced bill of materials itself: the quantity of the existing line
is changed, the matching line is removed, or a new line is created.
Nothing reaches the BOM before the approval, and a reset brings a
refused or already applied request back to draft for a new round. The
module is multi-company from the start, depends only on standard base,
mail and mrp, and needs no Enterprise module.

* ECO number, requester, approver and effective date per change.
* Change lines typed add, remove or change, with old and new quantity.
* Existing BOM selected explicitly or by default on the product template.
* Draft, review, approved, applied and refused workflow in the chatter.
* Apply writes the BOM: quantity change, line creation or removal.
* Application blocked until the request is approved.
* Reset to draft for refused or already applied requests.
* Multi-company, no Enterprise dependency, no external Python library.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Supply Chain/Manufacturing',
    'license': 'OPL-1',
    'price': 149.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'mrp',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/eco_request_0_views.xml',
        'views/eco_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
