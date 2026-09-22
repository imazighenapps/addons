from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestAutomationConfig(models.Model):
    _name = 'pest.automation.config'
    _description = 'PestOps Automation Configuration'
    _inherit = ['mail.thread']
    _order = 'company_id'

    name = fields.Char(required=True, default=lambda self: _('Automation Settings'))
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        ondelete='cascade',
    )
    visit_reminder_hours = fields.Integer(
        string='Visit Reminder (hours)',
        default=24,
        required=True,
        tracking=True,
        help='Create an activity for upcoming scheduled visits inside this window.',
    )
    contract_renewal_days = fields.Integer(
        string='Contract Renewal Window (days)',
        default=30,
        required=True,
        tracking=True,
    )
    overdue_anomaly_grace_days = fields.Integer(
        string='Anomaly Grace Period (days)',
        default=0,
        required=True,
        tracking=True,
    )
    overdue_visit_enabled = fields.Boolean(default=True, tracking=True)
    stock_alert_enabled = fields.Boolean(default=True, tracking=True)
    customer_notifications = fields.Boolean(
        string='Enable Customer Email Notifications',
        default=False,
        tracking=True,
    )
    customer_visit_reminders = fields.Boolean(default=False, tracking=True)
    customer_contract_renewals = fields.Boolean(default=True, tracking=True)
    customer_service_requests = fields.Boolean(default=True, tracking=True)
    customer_portal_documents = fields.Boolean(default=True, tracking=True)
    service_request_responsible_id = fields.Many2one(
        'res.users',
        string='Service Request Responsible',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    escalation_user_id = fields.Many2one(
        'res.users',
        string='Escalation Responsible',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        (
            'company_unique',
            'unique(company_id)',
            'Only one active PestOps automation configuration is allowed per company.',
        ),
    ]

    @api.constrains('visit_reminder_hours', 'contract_renewal_days', 'overdue_anomaly_grace_days')
    def _check_positive_windows(self):
        for rec in self:
            if rec.visit_reminder_hours <= 0:
                raise ValidationError(_('Visit reminder window must be greater than zero.'))
            if rec.contract_renewal_days < 0:
                raise ValidationError(_('Contract renewal window cannot be negative.'))
            if rec.overdue_anomaly_grace_days < 0:
                raise ValidationError(_('Anomaly grace period cannot be negative.'))

    @api.model
    def get_or_create_for_company(self, company=None):
        company = company or self.env.company
        record = self.search([('company_id', '=', company.id)], limit=1)
        if record:
            return record
        return self.create({
            'name': _('Automation Settings - %s') % company.display_name,
            'company_id': company.id,
        })
