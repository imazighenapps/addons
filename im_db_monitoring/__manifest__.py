# -*- coding: utf-8 -*-
{
    'name': "IM Data Base Monitoring",

    'summary': """ A module for monitoring and saving long-term historical data of a PostgreSQL database in Odoo """,

    'description': """
        This module is designed to monitor the status of a PostgreSQL database and save long-term historical data 
        for analysis over time. It collects data on database status, query statistics, table sizes, and more. 
        The historical data is stored and can be analyzed  showing trends over a longer period (30 minutes or more).
    """,

    'author': "Farid SLIMANI",
    'website': "",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 50.0,
    'category': 'Tools',
    'version': '1.0',

    'depends': ['base'],
    'images': ['static/description/img.png'],
    # always loaded
    'data': [
        
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/db_monitoring.xml',
        'views/db_block_io_history.xml',
        'views/db_general_status_history.xml',
        'views/db_query_statistics_history.xml',
        'views/db_table_size_history.xml',
        'views/db_tuples_fetched_returned_history.xml',
        'views/db_tuples_history.xml',
      
        
       
        'menu/menu.xml',
       
  
    ],
    
    "assets": {
       
        "web.assets_backend": [
          
            'im_db_monitoring/static/src/components/**/*.js',
            'im_db_monitoring/static/src/components/**/*.xml',

        ],
       
    },


    
}
