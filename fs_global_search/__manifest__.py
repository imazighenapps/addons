# -*- coding: utf-8 -*-
{
    'name': "FS Global Search",

    'summary': """Global keyword-based search across multiple Odoo models""",
    'description': """
    Global Search for Odoo
    =======================

    This module allows users to perform fast and intelligent searches across multiple models in Odoo using a single keyword. 
    It enhances productivity by removing the need to navigate through different menus or know the technical names of models.

    Key Features:
    -------------
    - Search across all `Char`, `Text`, and `Many2one.name` fields
    - Supports searching multiple models at once
    - Automatically excludes system/technical models
    - Displays results in a dynamic and clean list
    - Direct access to records with a "Show" button
    - Computes the number of matching results
    - Easy to use and seamlessly integrated into Odoo

    Technical:
    ----------
    - Uses Transient Models (no persistent data stored)
    - Respects user access rights
    - No performance overhead
    - Compatible with Odoo 14.0 to 18.0 (Community & Enterprise)

    Ideal for:
    ----------
    - Admins, support teams, and power users
    - Large Odoo databases with many apps and models
    - Anyone who wants faster access to Odoo records

    Save time and improve your workflow with Global Search!
    """,

    'author': "Farid SLIMANI",
    'website': "",
    'license': 'OPL-1',
    'category': 'Tools',
    'version': '1.0',
    'depends': ['base'],  
    'images': ['static/description/img.png'],
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 69.0,

    'data': [
        'security/ir.model.access.csv',
    
        'views/global_search_config.xml',        

        'menu/menu.xml',  
    ],
  


}
