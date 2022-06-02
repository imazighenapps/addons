# -*- coding: utf-8 -*-

{
    'name': 'Employee Documents Request Management',
    'version': '1.0.0',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'summary': """This module allow your employees to request their documents and manage all this""",
    'description': """  """,
    'author': 'Imazighen',
    'website': '',
    'support': 'imazighenapps@gmail.com',
    'images': ['static/description/index.jpeg'],
 
    'category': 'Human Resources',
    'depends': ['hr'],
    'data':[
        'security/security.xml',
        'security/multi_company_security.xml',
        'security/ir.model.access.csv',
        'data/doc_request_sequence.xml',
        'views/doc_request.xml',
        'views/doc_type.xml',
        'wizard/rejected_reason.xml',
       
        'menu/menu.xml',
    ],
    'installable' : True,
    'application' : False,
}

