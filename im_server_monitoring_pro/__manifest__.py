# -*- coding: utf-8 -*-
{
    'name': 'IM Server Monitor Pro',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    "summary": "Real-time server monitoring dashboard with system metrics, alerts, and process management",
    'description': """Server Monitor Pro for Odoo 18

           Advanced server monitoring module with:

           - Real-time CPU & RAM monitoring with historical data

           - Network monitoring (upload/download per interface)

           - Storage monitoring (disks)

           - Process management (list + secure kill)

           - Configurable alerts based on thresholds

           - Notifications via email and within Odoo

           - Dashboard with visually colored indicators (green/orange/red)

           - Interactive charts (real-time + 24h/7d/30d history)
    """,
        'author': 'Farid SLIMANI',
        'website': 'imazighenapps@gmail.com',
        'license': 'OPL-1',
        'price': 49.00,
        'currency': 'EUR',
        'depends': ['base', 'mail', 'web'],

    'data': [
        
        'security/server_monitor_security.xml',
        'security/ir.model.access.csv',
        'data/server_monitor_cron.xml',
        'data/server_monitor_data.xml',
        'wizards/server_monitor_kill_wizard.xml',
        'views/server_monitor_dashboard_views.xml',
        'views/server_monitor_config_views.xml',
        'views/server_monitor_history_views.xml',
        'views/server_monitor_alert_views.xml',
        'views/server_monitor_process_views.xml',
        'views/server_monitor_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'im_server_monitoring_pro/static/src/css/server_monitor.css',
            'im_server_monitoring_pro/static/src/xml/main.xml',
            'im_server_monitoring_pro/static/src/js/server_monitor_dashboard.js',
            'im_server_monitoring_pro/static/src/lib/chart.min.js',
        ],
    },
    'images': ['static/description/img.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['psutil'],
    },
}
