# -*- coding: utf-8 -*-
{
    'name': 'AI-Powered Inventory Forecasting',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Intelligent inventory forecasting using machine learning algorithms',
    'description': """
AI-Powered Inventory Forecasting
=================================

Predict future demand with 85-95% accuracy using advanced ML algorithms.

Features:
- Prophet, ARIMA, and Ensemble forecasting
- Automatic seasonality detection
- Intelligent stockout/overstock alerts
- Optimized reorder point calculations
- Interactive dashboards
- Multi-warehouse support
    """,
    
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'price': 249.00,
    'currency': 'EUR',
    
    'depends': [
        'base',
        'stock',
        'sale_management',
        'purchase',
        'web',
    ],
    
    'external_dependencies': {
        'python': ['prophet', 'pmdarima', 'statsmodels', 'scikit-learn', 'numpy', 'pandas'],
    },
    
    'data': [
        # Security
        'security/forecast_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/forecast_cron.xml',
        
        # Views
        'views/forecast_config_views.xml',
        'views/forecast_prediction_views.xml',
        'views/forecast_alert_views.xml',
        'views/forecast_reorder_views.xml',
        'views/product_views.xml',
        'views/forecast_dashboard_views.xml',

     
        
        # Wizards
        'wizards/generate_forecast_wizard_views.xml',
        
        # Reports
        'report/forecast_report.xml',


        'views/forecast_menus.xml',
    ],
    
    'assets': {
        'web.assets_backend': [
            'ai_inventory_forecast/static/src/css/forecast_dashboard.css',
            'ai_inventory_forecast/static/src/js/forecast_dashboard.js',
            'ai_inventory_forecast/static/src/xml/forecast_dashboard.xml',
        ],
    },
    'images': ['static/description/img.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
