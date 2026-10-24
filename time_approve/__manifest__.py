# -*- coding: utf-8 -*-
{
    'name': 'TimeApprove - Weekly Timesheet Approval',
    'version': '18.0.1.0.0',
    'summary': 'Weekly timesheet submission, manager approval, rejection comments and locking, so approved hours can no longer be edited.',
    'description': '''TimeApprove - Weekly Timesheet Approval
=======================================
Stop chasing timesheets at the end of the month.

TimeApprove groups timesheets by employee and by week. The employee submits
the week, the manager approves or rejects it with a comment, and approved
hours are locked: nobody can change them anymore. A reminder lists every week
that is still waiting.

* Weekly timesheet grouped by employee.
* Submit, approve, reject with a comment.
* Approved hours are locked against any modification.
* Reminder for weeks that are still waiting.
* Full history: who submitted, who approved, when.
* Total hours and billable amount per week.
* Works with the standard Odoo timesheet lines.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Services/Timesheets',
    'license': 'OPL-1',
    'price': 49.0,
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
        'views/timesheet_week_0_views.xml',
        'views/menus.xml',
        'data/cron.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
