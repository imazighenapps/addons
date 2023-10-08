{
    "name": "FS Dashboard Access rights",
    "summary": "Dinamic Dashboards Access Rights ",
    "version": "16.0.1.0.0",
    "category": "tools",
    "website": "",
    "author": "Farid SLIMANI",
    "license": "LGPL-3",
    'currency': 'EUR',
    'price': 20.0,
    "installable": True,
    'images': ['static/description/dashboard.png'],
    "depends": ["fs_dashboard",],
    "data": [
            'security/ir.model.access.csv',
            'security/res_groups.xml',
            'views/dashboard_config.xml',  
            'views/dashboard_item.xml',  
            
            
            'menu/menu.xml',
         
         ],


    "assets": {
       
        "web.assets_frontend": [
            
            ],

        "web.assets_backend": [

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
