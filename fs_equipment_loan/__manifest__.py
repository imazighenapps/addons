# -*- coding: utf-8 -*-
{
    'name': 'EquipLoan',
    'version': '19.0.1.0.0',
    'summary': 'Register equipment and tool loans to employees, track checkout and due dates, capture returns with condition, and keep overdue or ongoing loans visible in a company-safe register.',
    'description': '''EquipLoan - Equipment and Tool Loans to Employees
================================================
Laptops, tools and shared equipment move between employees with little trace:
items go missing, returns are late and nobody can answer who holds a device
right now.

EquipLoan provides a simple loan register. Maintain a catalogue of loanable
equipment, check items out to employees with an expected return date and record
the return with its condition and notes. Ongoing and overdue loans stay visible
so the responsible team can follow up before items are lost.

* Equipment catalogue with reference, category and active flag.
* Loan records linking an employee to equipment with checkout and due date.
* Workflow: draft, ongoing, returned, cancelled.
* Return capture with date, condition and notes.
* Overdue flag and views for ongoing and late loans.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/equipment_loan_0_views.xml',
        'views/equipment_loan_item_1_views.xml',
        'views/menus.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
