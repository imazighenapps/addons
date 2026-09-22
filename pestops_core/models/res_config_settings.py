from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pestops_default_frequency_type = fields.Selection(
        related='company_id.pestops_default_frequency_type',
        readonly=False,
    )
    pestops_default_frequency_number = fields.Integer(
        related='company_id.pestops_default_frequency_number',
        readonly=False,
    )
    pestops_default_visit_duration_minutes = fields.Integer(
        related='company_id.pestops_default_visit_duration_minutes',
        readonly=False,
    )
    pestops_default_plan_horizon_days = fields.Integer(
        related='company_id.pestops_default_plan_horizon_days',
        readonly=False,
    )
    pestops_visit_reminder_hours = fields.Integer(
        related='company_id.pestops_visit_reminder_hours',
        readonly=False,
    )
    pestops_contract_renewal_days = fields.Integer(
        related='company_id.pestops_contract_renewal_days',
        readonly=False,
    )
    pestops_anomaly_overdue_grace_days = fields.Integer(
        related='company_id.pestops_anomaly_overdue_grace_days',
        readonly=False,
    )
    pestops_require_inspection_before_close = fields.Boolean(
        related='company_id.pestops_require_inspection_before_close',
        readonly=False,
    )
    pestops_require_treatment_before_close = fields.Boolean(
        related='company_id.pestops_require_treatment_before_close',
        readonly=False,
    )
    pestops_auto_publish_reports = fields.Boolean(
        related='company_id.pestops_auto_publish_reports',
        readonly=False,
    )
    pestops_portal_documents_enabled = fields.Boolean(
        related='company_id.pestops_portal_documents_enabled',
        readonly=False,
    )
    pestops_automation_enabled = fields.Boolean(
        related='company_id.pestops_automation_enabled',
        readonly=False,
    )

    pestops_require_customer_signature_before_close = fields.Boolean(
        related='company_id.pestops_require_customer_signature_before_close',
        readonly=False,
    )
    pestops_enforce_mobile_geofence = fields.Boolean(
        related='company_id.pestops_enforce_mobile_geofence',
        readonly=False,
    )
    pestops_mobile_geofence_radius_meters = fields.Integer(
        related='company_id.pestops_mobile_geofence_radius_meters',
        readonly=False,
    )
