# -*- coding: utf-8 -*-
{
    'name': 'NoiseExposureLog',
    'version': '20.0.1.0.0',
    'summary': 'Record noise measurements with area, level, exposure duration, limit and exceedance flag.',
    'description': '''NoiseExposureLog - Workplace Noise Measurement Register
=======================================================
Noise readings kept in folders make exceedances and corrective actions hard to
follow.

NoiseExposureLog provides a simple measurement register.

* Measurements with area, date and optional employee.
* Measured level in dB and exposure duration.
* Configurable limit with automatic exceedance flag.
* Responsible measurer and notes.
* Draft, recorded, action required and cancelled states.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/noise_exposure_log_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
