{
    "name": "ShiftFlow - Digital Shift Handover",
    "version": "19.0.1.3.0",
    "category": "Operations",
    "summary": "Digital shift handovers, operational logs, incidents and carry-over actions",
    "description": "Digitize shift operations, capture incidents and logs, manage follow-up actions, and transfer outstanding work between outgoing and incoming teams.",
    "author": "Farid SLIMANI",
    "website": "https://slimanifarid.github.io",
    "license": "LGPL-3",
    'price': 58.00,
    'currency': 'EUR',
    "depends": ["base", "mail"],
    "data": [
        "security/shiftflow_security.xml",
        "security/ir.model.access.csv",
        "data/shiftflow_data.xml",
        "data/shiftflow_cron.xml",
        "data/shiftflow_mail.xml",
        "views/shift_team_views.xml",
        "views/shift_log_views.xml",
        "views/shift_incident_views.xml",
        "views/shift_task_views.xml",
        "views/shift_shift_views.xml",
        "views/shift_handover_views.xml",
        "views/shift_menus.xml",
        "report/handover_report.xml"
    ],
    "demo": ["demo/shiftflow_demo.xml"],
    "assets": {
        "web.assets_backend": [
            "shiftflow/static/src/js/shiftflow_dashboard.js",
            "shiftflow/static/src/xml/shiftflow_dashboard.xml",
            "shiftflow/static/src/scss/shiftflow_dashboard.scss"
        ]
    },
    "images": ["static/description/banner.png", "static/description/icon.png"],
    "installable": True,
    "application": True,
}
