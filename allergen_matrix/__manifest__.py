# -*- coding: utf-8 -*-
{
    'name': 'AllergenDesk',
    'version': '18.0.1.0.0',
    'summary': 'Build the allergen matrix of your recipes and the cross-contact rules auditors ask you to demonstrate.',
    'description': '''AllergenDesk - Allergens, Declared
==================================
Recipes change faster than labels. An ingredient is swapped, a line is
reworked, and the allergen declaration no longer matches what the
product contains or what may touch it on the same line. When an auditor
asks for the allergen matrix of a recipe, the answer is rebuilt from
memory, supplier sheets and a spreadsheet that nobody trusts.

AllergenDesk keeps one Odoo record per recipe: the product, the line and
the reference of the declaration you put on pack. Each recipe carries
its allergen lines: the allergen, whether it is present as an ingredient
or only as a possible cross-contact, and a short note on the source.
Counters for present allergens and cross-contact risks are computed and
stored on the recipe so the matrix can be filtered and reviewed at a
glance. Validating the recipe freezes the declaration, and the full
history stays in the chatter for the next audit.

* One recipe record per product with line and declaration reference.
* Allergen lines with allergen, presence type and source note.
* Counters for present and cross-contact allergens stored on the recipe.
* Draft, validated and archived states with an audit trail.
* Validating the recipe freezes the declaration from silent edits.
* Duplicate allergen entries on the same recipe are refused for you.
* A recipe without any allergen line cannot be validated.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
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
        'views/allergen_recipe_0_views.xml',
        'views/allergen_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
