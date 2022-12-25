# -*- coding: utf-8 -*-
{
    'name': "IM Server Monitoring",

    'summary': """ """,

    'description': """
        
    """,

    'author': "Farid SLIMANI",
    'website': "",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 10.0,
    'category': 'Tools',
    'version': '1.0',

    'depends': ['base'],
    'images': ['static/description/cpu_icon.PNG'],
    # always loaded
    'data': [
        
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/server_monitoring.xml',
       
      
        
       
        'menu/menu.xml',
       
  
    ],

    'qweb': ['static/src/xml/template.xml'],
  
}
