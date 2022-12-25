# -*- coding: utf-8 -*-
{
    'name' : 'Server Management Info',
    'version' : '1.1',
    'summary': 'Management of VM and physical machines, password, services and users',
    'sequence': 15,
    'description': """ """,
    'website': "",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 14.0,
    'category': 'Tools',
    'author': "Farid SLIMANI",
    'depends': ['base'],
    'images': ['static/description/index.jpg'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/res_server.xml',
        'views/res_service.xml',
        'menu/menu.xml',
       
    ],
    
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
}
