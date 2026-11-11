# -*- coding: utf-8 -*-
{
    'name': 'DocFlow',
    'version': '18.0.1.0.0',
    'summary': 'Distribute each controlled document revision to the right people and collect the acknowledgements ISO wants.',
    'description': '''DocFlow - Read, Signed, Compliant
=================================
A controlled procedure changes and the new revision lives in a shared
folder: some people read it, some never saw it, and the quality audit
asks for proof that everyone affected actually acknowledged the change.
The distribution list is a spreadsheet, the signatures are emails, and
nobody can tell which revision is the one in force.

DocFlow keeps one Odoo register per controlled document: its code, its
current revision and the date it became effective. Each distribution
line names the recipient, records when the document was sent and stamps
the acknowledgement when the person confirms they have read it. Open
distribution lines show who still has to sign instead of who might have
seen the email. When the auditor asks for evidence, the acknowledgement
list is the proof the module already holds.

* A register of controlled documents with code, revision and effective date.
* Distribution lines with recipient, sent date and acknowledgement date.
* Acknowledgements stamped with the exact date the recipient confirmed.
* Open and acknowledged counts computed and stored on every document.
* One pending-acknowledgements screen for everyone who still has to sign.
* An acknowledgement before the sent date is refused for you.
* A sent date in the future of the document timeline is kept consistent.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/doc_control_0_views.xml',
        'views/doc_distribution_1_views.xml',
        'views/doc_pending_2_views.xml',
        'views/menus.xml',
        'views/doc_pending_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
