# -*- coding: utf-8 -*-
{
    'name': 'AssetDisposalLog',
    'version': '18.0.1.0.0',
    'summary': 'Document asset disposal requests with method, values, requester, approver and tracked states.',
    'description': '''AssetDisposalLog - Asset Disposal Authorization Register
========================================================
Disposal approvals handled by email lose the reason and value trail.

AssetDisposalLog provides a simple disposal authorization register.

* Disposal records with asset reference, description and category.
* Disposal method: sale, scrap, donation, return.
* Disposal date, acquisition value and residual value.
* Requester, approver and reason.
* Draft, submitted, approved, disposed and cancelled states.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/asset_disposal_log_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
