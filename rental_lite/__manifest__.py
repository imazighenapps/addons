# -*- coding: utf-8 -*-
{
    'name': 'RentalLite - Equipment Rental for Odoo Community',
    'version': '19.0.1.0.0',
    'summary': 'Rent equipment with availability control, deposit, contract, return inspection and invoicing, without the Enterprise Rental app.',
    'description': '''RentalLite - Equipment Rental for Odoo Community
================================================
Rent out equipment, machines or event material without Excel.

RentalLite adds a lightweight rental cycle on top of Odoo Community: a rental
product with the number of units you own, a contract with a start and end
date, an availability check that refuses double bookings, a refundable
deposit, a return with inspection and damage fee, and an invoice in one click.

* Rental products with daily price and owned quantity.
* Availability check: no double booking of the same unit.
* Rental contract with start date, end date and automatic day count.
* Refundable deposit and damage fee at return.
* Return inspection: good, damaged, lost.
* One-click invoice with rental lines and deposit.
* Overdue detection on the contract list.
* Multi-company and multi-currency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 149.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
        'account',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/rental_contract_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
