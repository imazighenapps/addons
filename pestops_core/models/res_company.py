from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    pestops_default_frequency_type = fields.Selection(
        [
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
        ],
        string='Default Visit Frequency',
        default='weeks',
    )
    pestops_default_frequency_number = fields.Integer(
        string='Default Frequency Value',
        default=2,
    )
    pestops_default_visit_duration_minutes = fields.Integer(
        string='Default Visit Duration (min)',
        default=60,
    )
    pestops_default_plan_horizon_days = fields.Integer(
        string='Default Visit Generation Horizon (days)',
        default=60,
    )
    pestops_visit_reminder_hours = fields.Integer(
        string='Visit Reminder (hours)',
        default=24,
    )
    pestops_contract_renewal_days = fields.Integer(
        string='Contract Renewal Warning (days)',
        default=30,
    )
    pestops_anomaly_overdue_grace_days = fields.Integer(
        string='Anomaly Grace Period (days)',
        default=0,
    )
    pestops_require_inspection_before_close = fields.Boolean(
        string='Require Inspection Before Visit Completion',
        default=True,
    )
    pestops_require_treatment_before_close = fields.Boolean(
        string='Require Treatment Before Visit Completion',
        default=False,
    )
    pestops_auto_publish_reports = fields.Boolean(
        string='Auto-Publish Service Reports',
        default=True,
    )
    pestops_portal_documents_enabled = fields.Boolean(
        string='Enable Portal Documents',
        default=True,
    )
    pestops_automation_enabled = fields.Boolean(
        string='Enable PestOps Automations',
        default=True,
    )

    pestops_require_customer_signature_before_close = fields.Boolean(
        string='Require Customer Signature Before Visit Completion',
        default=False,
    )
    pestops_enforce_mobile_geofence = fields.Boolean(
        string='Enforce Mobile Geofence',
        default=False,
    )
    pestops_mobile_geofence_radius_meters = fields.Integer(
        string='Mobile Geofence Radius (m)',
        default=250,
    )
