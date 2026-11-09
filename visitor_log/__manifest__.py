# -*- coding: utf-8 -*-
{
    'name': 'VisitorLog',
    'version': '20.0.1.0.0',
    'summary': 'Sign visitors in and out at the front desk, record who hosts them, and purge the register automatically after the retention period your policy allows.',
    'description': '''VisitorLog - Front Desk Register
================================
A supplier waits in the hall, somebody signs the paper register, and the
page is never looked at again. At the security audit nobody can say who
entered the building last Tuesday, which employee was expecting the visitor,
or how long the technician stayed in the server room.

VisitorLog replaces the paper register with an Odoo record created in a few
seconds at the front desk: the visitor, their company, a phone and an email,
the employee who hosts them and the purpose of the visit - meeting,
delivery, interview, maintenance or other. A badge number is handed out, the
check-in time is stamped, and one button checks the visitor out and computes
the time spent on site. The Host view groups the same register by employee,
so reception can see who is expected today and who is still inside. A purge
wizard deletes the visits checked out before a chosen date, for the current
company only, which is exactly what a retention policy asks for.
 
* Front desk register with visitor, company, phone and email.
* Host per visit, with a grouped view by employee.
* Purpose of the visit: meeting, delivery, interview, maintenance, other.
* Badge number, check-in and check-out timestamps.
* Duration on site computed and stored on every visit.
* Expected, on site, checked out and cancelled states.
* Purge wizard by check-out date, restricted to the current company.
* Multi-company isolation, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/visitor_log_0_views.xml',
        'views/visitor_host_1_views.xml',
        'views/visitor_purge_2_views.xml',
        'views/menus.xml',
        'views/visitor_host_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
