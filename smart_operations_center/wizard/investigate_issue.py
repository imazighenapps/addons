from odoo import fields, models


class SmartOperationsInvestigateWizard(models.TransientModel):
    _name = 'smart.operations.investigate.wizard'
    _description = 'Investigate Operational Issue'

    issue_id = fields.Many2one('smart.operations.issue', required=True)
    findings = fields.Text(required=True)
    next_action = fields.Selection([
        ('action_required', 'Action Required'), ('escalated', 'Escalate'), ('resolve', 'Resolve'),
    ], default='action_required', required=True)

    def action_confirm(self):
        self.ensure_one()
        self.issue_id.message_post(body=self.findings)
        self.issue_id.state = self.next_action
        if self.next_action == 'resolve':
            self.issue_id.action_resolve()
        return {'type': 'ir.actions.act_window_close'}
