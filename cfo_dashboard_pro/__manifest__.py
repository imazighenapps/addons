# -*- coding: utf-8 -*-
{
    'name': 'Smart Financial Dashboard - CFO Pack Pro',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Executive Financial Dashboard with Cash Flow Forecast, Profitability Analysis & Multi-Company Consolidation',
    'description': """
Smart Financial Dashboard - CFO Pack Pro
=========================================

Transform your financial data into strategic insights with AI-powered forecasting.

**Key Features:**

Executive Financial Cockpit
---------------------------
* Real-time KPIs: Revenue, Margins, EBITDA, Cash Position
* Drill-down capabilities on all metrics
* Multi-dimensional analysis

Cash Flow Forecast Engine
--------------------------
* 180-day intelligent projection
* Machine learning-based payment predictions
* Scenario analysis (optimistic/pessimistic/realistic)
* Visual cash runway calculator

Advanced Profitability Analysis
--------------------------------
* Multi-dimensional margin analysis (product, customer, project, territory)
* Support for Standard, FIFO, AVCO costing methods
* Indirect cost allocation engine
* Contribution margin by segment

Financial Performance Intelligence
-----------------------------------
* DSO/DPO/DIO calculation and trending
* Aging analysis with risk scoring
* Customer concentration risk analysis
* Working capital optimization

Multi-Company Consolidation
----------------------------
* Automatic intercompany elimination
* Multi-currency consolidation
* Group vs subsidiary comparison
* Consolidated P&L and Balance Sheet

Smart Alerting System
----------------------
* Configurable financial thresholds
in-app notifications
* Automated board reports (PDF/Excel)
* Custom alert rules

**Perfect for:**
* CFOs, Controllers, Financial Analysts
* CEOs requiring strategic financial visibility
* Accountants and financial consultants
* SMBs to mid-market companies

**Technical Excellence:**
* Optimized SQL with materialized aggregations
* Smart caching for instant dashboard loads
* OWL framework for modern UX
* Full Community & Enterprise compatibility
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'price': 199.00,
    'currency': 'EUR',
    'depends': [
        'base',
        'account',
        'sale_management',
        'purchase',
        'stock',
        'analytic',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/cron.xml',
        'data/default_config.xml',
        'data/alert_templates.xml',
        
        # Views
        'views/dashboard_views.xml',
        'views/config_views.xml',
        'views/cashflow_views.xml',
        'views/profitability_views.xml',
        'views/risk_views.xml',
        'views/consolidation_views.xml',
        'views/menu_views.xml',
        
        # Reports
        'reports/board_report_template.xml',
        'reports/cashflow_report_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cfo_dashboard_pro/static/src/js/**/*',
            'cfo_dashboard_pro/static/src/components/**/*',
            'cfo_dashboard_pro/static/src/xml/**/*',
            'cfo_dashboard_pro/static/src/scss/**/*',
        ],
    },
  
    'images': ['static/description/img.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
