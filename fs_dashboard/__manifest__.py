{
    "name": "FS Dashboard",
    "summary": "Module for dynamically creating dashboards",
    "version": "16.0.1.0.0",
    "category": "tools",
    "website": "",
    "author": "Farid SLIMANI",
    "license": "LGPL-3",
    "installable": True,
    'images': ['static/description/appointment.jpg'],
    "depends": ["base",],
    "data": [
             'security/ir.model.access.csv',
             'views/dashboard_show.xml',
             'views/dashboard_confing.xml',
             'views/dashboard_item.xml',
             'menu/menu.xml',
         
         ],


    "assets": {
       
        "web.assets_frontend": [
            
            ],

        "web.assets_backend": [
            'fs_dashboard/static/src/js/dashboard_show.js',
            'fs_dashboard/static/src/css/dashboard_show.css',
        
            'fs_dashboard/static/src/xml/main.xml',
            'fs_dashboard/static/src/xml/dashboard_tile.xml',
            'fs_dashboard/static/src/xml/chart_view.xml',
           

        ],
        "web.assets_qweb": [
          
        ],
        
        'web._assets_primary_variables': [
          
        ],

        "web.assets_tests": [
            
        ],
    },
    "sequence": 1,
}
