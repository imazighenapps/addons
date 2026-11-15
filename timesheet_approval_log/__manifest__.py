# -*- coding: utf-8 -*-
{
    'name': 'TimesheetApproval',
    'version': '18.0.1.0.0',
    'summary': 'Track timesheet period submissions per employee with draft, submitted, approved and rejected states, totals and approver comments.',
    'description': '''TimesheetApproval - Submission and Approval Log
================================================
Timesheet lines are entered continuously, but the handoff from employee
submission to manager approval is often informal and hard to audit.

TimesheetApproval records each submission period per employee with an explicit
state, total hours, approver and comments.

* Submission log per employee and period.
* Draft, submitted, approved and rejected states.
* Total hours computed for the period and employee.
* Approver, submission date, approval date and comments.
* Linked employee and optional project context.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Timesheets',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'hr_timesheet',
        'project',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/timesheet_approval_log_0_views.xml',
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
