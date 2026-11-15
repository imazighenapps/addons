# -*- coding: utf-8 -*-
{
    'name': 'VisitorMealLog',
    'version': '19.0.1.0.0',
    'summary': 'Record visitor and guest meals with host, date, quantity, details and states to coordinate and track provided meals.',
    'description': '''VisitorMealLog - Visitor and Guest Meal Register
================================================
Visitor meals arranged informally are hard to track and reconcile.

VisitorMealLog provides a simple register of meal requests and servings.

* Meal records with host, date and number of meals.
* Visitor/guest details and meal type or notes.
* Location or meeting reference.
* Draft, requested, served and cancelled states.
* Meal history.
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
        'views/visitor_meal_log_0_views.xml',
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
