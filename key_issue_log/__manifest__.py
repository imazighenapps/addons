# -*- coding: utf-8 -*-
{
    'name': 'KeyIssueLog',
    'version': '19.0.1.0.0',
    'summary': 'Record physical key issues and returns with holder, dates, condition notes and states to keep a clear custody history.',
    'description': '''KeyIssueLog - Key Issue and Return Register
===========================================
Physical keys issued informally are easy to lose track of, creating security
and replacement risks.

KeyIssueLog keeps a simple register of key handovers and returns.

* Key records with identifier/label and holder.
* Issue, expected return and actual return dates.
* Responsible issuer and condition notes.
* Draft, issued, returned and lost states.
* Key handover history.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 19.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'contacts',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/key_issue_log_0_views.xml',
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
