# -*- coding: utf-8 -*-

from . import models
from . import wizards
from . import algorithms


def post_init_hook(env):
    """Post-installation hook to setup initial data"""
    # Create default configuration if none exists
    configs = env['forecast.config'].search([])
    if not configs:
        env['forecast.config'].create({
            'name': 'Default Configuration',
            'algorithm': 'ensemble',
            'forecast_horizon': 90,
            'confidence_level': 0.95,
            'enable_seasonality': True,
            'enable_holidays': True,
            'retrain_frequency': 'weekly',
            'min_history_days': 90,
            'active': True,
        })


def uninstall_hook(env):
    """Cleanup on module uninstallation"""
    # Archive all predictions and alerts
    env['forecast.prediction'].search([]).write({'active': False})
    env['forecast.alert'].search([]).write({'active': False})
