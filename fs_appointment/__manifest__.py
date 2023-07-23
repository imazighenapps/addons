# -*- coding: utf-8 -*-
{
    'name': "FS Appointment",
    'summary': """ """,
    'description': """  """,
    'author': "SLIMANI Farid",
    'website': "",
    'category': 'Appointment',
    'version': '1.0',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 22.0,
    'sequence': 5,
    'depends': ['base','hr','contacts'],

 
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'views/appointment.xml',
        'views/calendar.xml',
        'views/holiday.xml',
        'views/notification.xml',
        'views/service.xml',
       
        

        
        'menu/menu.xml',

       
    ],
     'demo': [
        'data/data_appointment.xml',
    ],

    'application': True,
}


