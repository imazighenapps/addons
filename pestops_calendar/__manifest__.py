{
    'name': 'PestOps Calendar',
    'version': '19.0.1.0.1',
    'category': 'Services',
    'summary': 'Community scheduling and conflict control for PestOps visits',
    'description': '''
Adds Community-native calendar planning to PestOps visits.

Features:
- Calendar view of PestOps visits.
- Technician-based calendar coloring.
- Planning filters for today, week, status and conflicts.
- Conflict detection for overlapping visits assigned to the same technician.
- Scheduling/start actions blocked when a technician has an overlapping visit.
- No Enterprise-only dependency.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'calendar',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'views/pest_calendar_views.xml',
        'views/pest_calendar_menus.xml',
    ],
    'application': False,
    'installable': True,
}
