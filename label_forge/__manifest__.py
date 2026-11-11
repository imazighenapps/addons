# -*- coding: utf-8 -*-
{
    'name': 'LabelForge',
    'version': '20.0.1.0.0',
    'summary': 'Design the product, lot and location labels your warehouse needs and print them straight from Odoo.',
    'description': '''LabelForge - Labels Straight From Odoo
======================================
Warehouse labels live in scattered templates: a spreadsheet for products, a
separate file for locations, and a manual edit every time a lot label is
needed. The result is inconsistent barcodes, wrong sizes and no trace of
what was actually printed.

LabelForge lets you design label templates in Odoo and log every print run.
Each template defines the label type, size and content fields, while print
jobs record the target, the quantity and the outcome. Teams can keep a clean
library of product, lot and location labels and know exactly what left the
printer.

* A label template library for product, lot and location labels.
* Template settings for size, content and active status.
* A print job log with target, quantity and template reference.
* States to draft, print and cancel each label job.
* Stored counters linking templates to their print jobs.
* Search filters and group-by views for label type and status.
* Notes on templates and jobs for operational context.
* Multi-company isolation with per-company records.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
    'license': 'OPL-1',
    'price': 45.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/label_template_0_views.xml',
        'views/label_job_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
