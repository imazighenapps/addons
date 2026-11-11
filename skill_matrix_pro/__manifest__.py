# -*- coding: utf-8 -*-
{
    'name': 'SkillMap',
    'version': '18.0.1.0.0',
    'summary': 'Map who in the team holds which certified skill and expose the gaps the production plan depends on.',
    'description': '''SkillMap - Skills Gap, Named
============================
Production plans assume that the right skills are available, yet the
proof of who can do what is often spread across certificates, emails and
memory. When a machine stops or a shift changes, managers discover too
late that a required certification is missing or expired, and the gap
turns into downtime or a rushed subcontract.

SkillMap builds a clear matrix of skills and assignments in Odoo so
every certified capability is visible at a glance. Each skill defines
what is required, whether certification is mandatory and how many people
should hold it. Assignments link employees to skills with a level, a
certification date and an optional expiry, making it easy to see who is
covered and where the team is exposed.

With stored counters and simple filters, SkillMap turns informal
knowledge into a shared, auditable view of coverage and gaps that
supports planning, audits and training decisions.

* A catalog of skills with required coverage and certification rules.
* Employee assignments with level, certification and expiry dates.
* Stored counters of holders and valid certifications per skill.
* A workflow to certify, expire or revoke each assignment.
* Search filters for certified, expired and missing coverage cases.
* Grouping by skill and employee for matrix-style reviews.
* Constraints on levels, dates and duplicate assignments.
* Multi-company isolation with autonomous employee records in tests.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/skill_skill_0_views.xml',
        'views/skill_assignment_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
