# -*- coding: utf-8 -*-
{
    'name': 'JobCostPro - Job Costing, Committed Costs and Real Margin',
    'version': '19.0.1.0.0',
    'summary': 'Compare the budget of every job with its actual and committed costs, cap the progress at 100 percent and flag the job before an overrun destroys the margin.',
    'description': '''JobCostPro - Job Costing, Committed Costs and Real Margin
=========================================================
A job is sold at a healthy margin. Then the site manager orders three extra
pallets, the electrician sends a change order, and the subcontractor invoices
six weeks late. None of it shows in the margin until the job is closed.

JobCostPro keeps the budget and the real cost of a job on one screen. Enter
the budget revenue and the budget cost when the job is won, then record every
cost line as it happens: labor, material, subcontract, overhead or other.
Each line can be marked as committed when it is already engaged - a purchase
order sent, a subcontract signed - but not yet invoiced. Actual cost only
counts invoiced lines, committed cost sums the engaged ones, and the margin is
computed as the revenue minus both, because a commitment already belongs to
somebody else even if the invoice is not in the mailbox yet. Progress is
measured against the budget cost and stays between 0 and 100 percent. When
actual plus committed cost exceeds the budget by more than the alert
threshold, the job is flagged as overrun before the next purchase order is
sent. Closing the job locks its budget and its lines, and every decision
stays in the chatter.

* Budget revenue and budget cost per job, linked to a customer and a project.
* Cost lines typed as labor, material, subcontract, overhead or other.
* Committed flag for costs engaged but not yet invoiced.
* Actual cost, committed cost, margin and margin rate, always up to date.
* Progress capped between 0 and 100 percent of the budget cost.
* Overrun alert on actual plus committed cost, above a configurable threshold.
* Draft, running and closed states with a full audit trail.
* Budget and cost lines locked once the job is closed, no Enterprise
  dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 149.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'project',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/job_cost_0_views.xml',
        'views/job_cost_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
