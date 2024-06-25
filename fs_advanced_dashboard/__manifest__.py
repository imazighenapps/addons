{
    "name": "FS Advenced Dashboard",
    "summary": "FS Advanced dashboard, module extension to add more features to basic dashboard",
    "version": "1.0",
    "category": "tools",
    "website": "",
    "author": "Farid SLIMANI",
    "license": "LGPL-3",
    'currency': 'EUR',
    'price': 40.0,
    'images': ['static/description/template1.png'],
    "installable": True,
    'images': [],
    "depends": ["base","fs_dashboard"],

    
    "data": [
          'views/dashboard_item.xml',
         ],


    "assets": {
       
        "web.assets_frontend": [
            
            ],

        "web.assets_backend": [
            'fs_advanced_dashboard/static/src/components/**/*.css',
            'fs_advanced_dashboard/static/src/components/**/*.js',
            'fs_advanced_dashboard/static/src/components/**/*.xml',
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
