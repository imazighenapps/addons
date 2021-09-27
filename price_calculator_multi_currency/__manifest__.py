# -*- coding: utf-8 -*-
{
    'name': "Price Calculator Multi Currency",

    'summary': """
       This module is involved in the calculation of prices in the lines of the invoice by changing the currency in invoice
            """,

    'description': """
       
    """,

    'author': "Imazighen",
    'website': "",
    "price": "5",
    "currency": "EUR",
    'category': 'account',
    'version': '1.13',
    'support': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move.xml',
    ],
    "images": [
        'static/description/home.png',
      
    ],
  
   
}
