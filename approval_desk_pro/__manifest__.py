# -*- coding: utf-8 -*-
{
    'name': 'ApprovalDeskPro',
    'version': '18.0.1.0.0',
    'summary': 'Route any record through a multi-level approval chain: one approver per amount threshold, strict step-by-step sign-off, dated decisions and a full chatter trail.',
    'description': '''ApprovalDeskPro - Multi-Level Approval Workflow
==============================================

Every purchase order above 5 000 EUR needs the team leader, above 20 000 EUR
the finance director, and above 50 000 EUR the general manager. In most Odoo
databases that rule lives in an email thread, in a shared spreadsheet, or in
the head of the person who has been there the longest.

ApprovalDeskPro gives that rule a home. A request records what is being
approved - any record of any application, referenced by its model, its
identifier and its display name - together with the amount, the requester and
the company. Each approver is attached to the request with a minimum amount,
so a single request carries its whole approval matrix. When the requester
submits, the chain is built automatically: only the approvers whose threshold
is reached by the amount are kept, in ascending order of threshold. Each of
them approves in turn, the next step opens only when the previous one has
signed, and the request becomes approved when the last approver has decided.
A refusal stops the chain immediately and the request is closed as refused.
Every decision is dated, signed and posted in the chatter, so the audit trail
is never reconstructed after the fact. The module works on any Odoo record and
never depends on another application, so the same chain can guard a purchase
order, a vendor bill, a discount or a recruitment offer. Amounts are kept in
the request currency and each company only sees its own requests.

* Approval request on any record: model name, record ID, display name.
* One approver per threshold, with a minimum amount.
* Chain built automatically at submission, ordered by threshold.
* Strict step-by-step approval: only the current approver can sign.
* Refusal closes the request and stops the whole chain.
* Reset to draft clears the chain and starts over.
* Dated decisions, comments and a full chatter history.
* Multi-company and multi-currency, no dependency on other applications.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Productivity',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/approval_desk_request_0_views.xml',
        'views/approval_desk_step_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
