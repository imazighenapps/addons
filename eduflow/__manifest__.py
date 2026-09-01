# -*- coding: utf-8 -*-
{
    'name': 'EduFlow - School Management',
    'version': '18.0.1.1.0',
    'category': 'Education',
    'summary': "Integrated school management solution: students, parents, admissions, "
               "enrollments, classes, timetables, attendance, exams, grades, "
               "report cards, fees and payments.",
    'description': """
EduFlow - School Information System (SIS)
===============================================

EduFlow centralizes the entire student lifecycle in Odoo:

* Institution setup, academic years and periods
* Student and parent/guardian management
* Admission workflow (application -> review -> interview -> acceptance)
* Enrollments, re-enrollments, class transfers
* Levels, classes, subjects, academic programs
* Timetable with conflict detection
* Attendance / absences with justification
* Exams, grades, automatic average calculation
* Printable report cards (PDF)
* School fees, payment schedules, payments and overdue tracking
* Role-based security (Admin, Management, Administration, Teacher, Accountant, Parent)
* Management dashboard
""",
    'author': 'EduFlow',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'depends': ['base', 'mail', 'portal', 'account', 'payment', 'website', 'website_payment', 'hr'],
    'data': [
        # security
        'security/eduflow_security.xml',
        'security/ir.model.access.csv',
        'security/eduflow_record_rules.xml',
        'security/eduflow_multicompany_rules.xml',
        # data
        'data/eduflow_sequences.xml',
        'data/eduflow_cron.xml',
        # views
        'views/eduflow_academic_year_views.xml',
        'views/eduflow_academic_period_views.xml',
        'views/eduflow_level_views.xml',
        'views/eduflow_classroom_views.xml',
        'views/eduflow_parent_views.xml',
        'views/eduflow_student_views.xml',
        'views/eduflow_document_type_views.xml',
        'views/eduflow_admission_views.xml',
        'views/eduflow_enrollment_views.xml',
        'views/eduflow_teacher_views.xml',
        'views/eduflow_subject_views.xml',
        'views/eduflow_program_views.xml',
        'views/eduflow_timetable_views.xml',
        'views/eduflow_timetable_config_views.xml',
        'views/eduflow_timetable_generate_wizard_views.xml',
        'views/eduflow_attendance_views.xml',
        'views/eduflow_attendance_wizard_views.xml',
        'views/eduflow_exam_views.xml',
        'views/eduflow_grade_views.xml',
        'views/eduflow_report_card_views.xml',
        'views/eduflow_fee_views.xml',
        'views/eduflow_payment_views.xml',
        'views/eduflow_dashboard_views.xml',
                'views/dashboard_education_views.xml',
        'views/eduflow_menus.xml',
        'views/eduflow_portal_templates.xml',
        'views/eduflow_public_admission_templates.xml',
        # reports
        'report/eduflow_report_card_report.xml',
        'report/eduflow_report_card_template.xml',
    ],
    'demo': [
        'data/eduflow_demo.xml',
        'data/eduflow_demo_western.xml',
        'data/eduflow_demo_complete.xml',
        'data/eduflow_demo_states.xml',
        'data/eduflow_demo_portal.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eduflow/static/src/scss/dashboard_education.scss',
            'eduflow/static/src/xml/dashboard_education.xml',
            'eduflow/static/src/js/dashboard_education.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 59.00,
    'currency': 'EUR',
}
