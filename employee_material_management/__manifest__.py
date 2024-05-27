# -*- coding: utf-8 -*-

{
    
    'name': 'Employee Material Acquisition Management',
    'version': '1.3.3',
    'price': 15.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'summary': """This module allow your employees to request material acquisition""",
    'description': """  """,
    'author': 'Farid SLIMANI',
    'website': '',
    'support': 'imazighenapps@gmail.com',
    'images': ['static/description/c_image.png'],
 
    'category': 'Human Resources',
    'depends': ['hr','stock','purchase'],
    'data':[
        'security/security.xml',
        'security/multi_company_security.xml',
        'security/ir.model.access.csv',
        'data/material_request_sequence.xml',
        'views/material_request.xml',
        'wizard/rejected_reason.xml',
        'wizard/create_po.xml',
        'wizard/create_picking.xml',
        'menu/menu.xml',
    ],
    'installable' : True,
    'application' : False,
}

