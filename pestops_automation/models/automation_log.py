from odoo import fields, models, _


class PestAutomationLog(models.Model):
    _name = 'pest.automation.log'
    _description = 'PestOps Automation Event Log'
    _order = 'event_at desc, id desc'

    name = fields.Char(required=True, copy=False)
    key = fields.Char(required=True, copy=False, index=True)
    event_type = fields.Selection([
        ('visit_reminder', 'Upcoming Visit Reminder'),
        ('visit_overdue', 'Overdue Visit'),
        ('contract_renewal', 'Contract Renewal'),
        ('anomaly_overdue', 'Overdue Anomaly'),
        ('stock_alert', 'Stock Alert'),
        ('service_request', 'Service Request'),
        ('portal_document', 'Portal Document'),
    ], required=True, index=True)
    company_id = fields.Many2one('res.company', required=True, index=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Responsible User', index=True)
    partner_id = fields.Many2one('res.partner', string='Customer', index=True)
    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)
    record_display_name = fields.Char()
    email_sent = fields.Boolean(default=False)
    activity_created = fields.Boolean(default=False)
    event_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    note = fields.Text()

    _sql_constraints = [
        ('key_unique', 'unique(key)', 'This automation event has already been logged.'),
    ]

    def action_open_record(self):
        self.ensure_one()
        if not self.res_model or not self.res_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Open Record'),
            'res_model': self.res_model,
            'view_mode': 'form',
            'res_id': self.res_id,
            'target': 'current',
        }
