# -*- coding: utf-8 -*-

from . import models
from . import services
from . import wizards
from . import reports


def post_init_hook(env):
    """Initialize module data after installation"""

    # Create default configuration
    Config = env['cfo.dashboard.config']
    if not Config.search([]):
        Config.create({
            'name': 'Default Configuration',
            'cashflow_projection_days': 180,
            'dso_rolling_months': 12,
            'risk_high_threshold': 80.0,
            'risk_medium_threshold': 50.0,
            'burn_rate_alert_threshold': -10000.0,
            'margin_alert_threshold': 20.0,
        })

    # Initialize snapshot for current month
    Snapshot = env['cfo.kpi.snapshot']
    Snapshot.compute_monthly_snapshot()

    # Schedule initial aggregation
    env['cfo.cashflow.projection'].rebuild_projections()