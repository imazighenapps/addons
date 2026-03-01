# -*- coding: utf-8 -*-
# ============================================================
# sentinelle_health_monitor/__manifest__.py
# Odoo 19 Health Monitor Module
# ============================================================
{
    'name': 'Sentinelle Health Monitor',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Real-time Odoo instance health monitoring, alerting & performance dashboard',
    'description': """
Sentinelle Health Monitor
=========================
A production-grade module that continuously monitors your Odoo instance and alerts
developers/admins before small issues become major outages.

Key Features
------------
* ORM Performance Monitoring: track slow create / write / search operations
* SQL Query Analysis: detect slow queries and N+1 patterns
* External API Response Time tracking
* Log Error Frequency Analysis
* Cron Job Health: detect delays and failures
* System Resources: CPU, RAM, disk usage (key tables)
* Multi-channel Alerts: Odoo dashboard + Email + Slack webhook
* Extensible Metric Framework: add new metrics with minimal code
* Beautiful dashboard with Kanban & List views, filterable by severity

Designed for Odoo CE & EE.
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
        'price': 229.00,
        'currency': 'EUR',

    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        # Security — always first
        'security/sentinelle_security.xml',
        'security/ir.model.access.csv',
      

        # Configuration data
        'data/sentinelle_config_data.xml',
        'data/sentinelle_cron_data.xml',
        'data/sentinelle_metric_threshold_data.xml',

        # Views
        'views/sentinelle_metric_views.xml',
        'views/sentinelle_alert_views.xml',
        'views/sentinelle_config_views.xml',
        'views/sentinelle_dashboard_views.xml',
        'views/sentinelle_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sentinelle_health_monitor/static/src/css/sentinelle.css',
            'sentinelle_health_monitor/static/src/css/sentinelle_dashboard.css',
            # OWL Dashboard component — QWeb XML templates
            'sentinelle_health_monitor/static/src/xml/sentinelle_dashboard.xml',
            # OWL Dashboard component — JS (KpiCard, GaugeWidget, AlertRow, SentinelleDashboard)
            'sentinelle_health_monitor/static/src/js/sentinelle_dashboard.js',
            
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
