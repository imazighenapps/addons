from odoo import fields, models


class SmartOperationsResolveWizard(models.TransientModel):
    _name = 'smart.operations.resolve.wizard'
    _description = 'Resolve Operational Issue'

    issue_id = fields.Many2one('smart.operations.issue', required=True)
    reason = fields.Text(required=True)

    def action_confirm(self):
        self.ensure_one()
        self.issue_id.write({
            'state': 'resolved', 'resolved_at': fields.Datetime.now(),
            'resolution_reason': self.reason,
        })
        self.issue_id.message_post(body=self.reason)
        return {'type': 'ir.actions.act_window_close'}
