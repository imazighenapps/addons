{
    "name": "FS Dashboard",
    "summary": "Module for dynamically creating dashboards",
    "version": "0.1",
    "category": "tools",
    "website": "",
    "author": "Farid SLIMANI",
    "license": "LGPL-3",
    "installable": True,
    'images': ['static/description/template1.PNG'],
    "depends": ["web","base_setup"],
    'uninstall_hook': "uninstall_hook",
    
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
            'fs_dashboard/static/src/components/**/*.css',
            'fs_dashboard/static/src/components/**/*.js',
            'fs_dashboard/static/src/components/**/*.xml',
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
