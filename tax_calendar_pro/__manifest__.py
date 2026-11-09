# -*- coding: utf-8 -*-
{
    'name': 'TaxCalendar',
    'version': '18.0.1.0.0',
    'summary': 'Generate every VAT, corporate tax and payroll deadline from simple recurrence rules, then track what is filed, paid or late in one dated calendar.',
    'description': '''TaxCalendar - Tax Deadlines Under Control
=========================================
VAT returns, corporate tax advances, payroll declarations and withholding
taxes all fall on dates that nobody remembers the same way twice. The
accountant keeps a spreadsheet, the calendar is rebuilt every January, and
the first late filing is discovered when the penalty letter arrives.

TaxCalendar turns the recurring obligation into a rule. For each tax type,
pick a frequency - monthly, quarterly or yearly - and the number of days
between the end of the period and the filing date. One click generates the
whole year: every period gets its start, its end and its due date, computed
deterministically, without duplicates when the generation is run again.
Each deadline is then followed on its own: upcoming, done or late, with the
number of days left, the amount to pay and a note. The list sums the amounts,
the search filters isolate what is late or still open, and the graph shows
where the effort sits by tax type and status. Everything is scoped per
company, so each entity of the group keeps its own calendar.

* Recurrence rules per tax type and frequency.
* Monthly, quarterly and yearly generation in one click.
* Due date derived from the period end and a configurable day offset.
* Upcoming, done and late states with the completion date.
* Late flag and days left, always visible on the deadline.
* Amount per deadline and totals in the list and the graph.
* Search filters on late, done and upcoming, grouped by tax type.
* Multi-company calendar with per-company rule uniqueness.
* No Enterprise dependency, no external library.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/tax_deadline_0_views.xml',
        'views/tax_rule_1_views.xml',
        'views/tax_calendar_wizard_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
