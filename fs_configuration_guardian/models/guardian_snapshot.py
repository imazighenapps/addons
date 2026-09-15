from odoo import api, fields, models, _


class GuardianSnapshot(models.Model):
    _name = 'fs.guardian.snapshot'
    _description = 'Configuration Guardian Snapshot'
    _order = 'captured_at desc, id desc'

    name = fields.Char(required=True)
    baseline_id = fields.Many2one('fs.guardian.baseline', index=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    captured_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    captured_by = fields.Many2one('res.users', required=True, default=lambda self: self.env.user)
    is_baseline = fields.Boolean(default=False)
    state = fields.Selection([('draft', 'Draft'), ('completed', 'Completed'), ('failed', 'Failed')], default='draft', required=True)
    item_count = fields.Integer(default=0)
    payload = fields.Json(default=dict)
    error_message = fields.Text()
    checksum = fields.Char(index=True)
    scan_type = fields.Selection([('baseline', 'Production Baseline'), ('scan', 'Configuration Scan')], default='scan', required=True)

    @api.model
    def create_from_current(self, baseline=None, is_baseline=False):
        from ..services.snapshot_service import GuardianSnapshotService
        company = baseline.company_id if baseline else self.env.company
        name = _('Baseline - %s') % fields.Datetime.now() if is_baseline else _('Snapshot - %s') % fields.Datetime.now()
        snapshot = self.create({
            'name': name,
            'baseline_id': baseline.id if baseline else False,
            'company_id': company.id,
            'captured_by': self.env.user.id,
            'is_baseline': is_baseline,
            'scan_type': 'baseline' if is_baseline else 'scan',
        })
        try:
            result = GuardianSnapshotService(self.env).capture(company=company)
            snapshot.write({
                'payload': result['payload'],
                'item_count': result['item_count'],
                'checksum': result['checksum'],
                'state': 'completed',
            })
        except Exception as exc:
            snapshot.write({'state': 'failed', 'error_message': str(exc)})
            raise
        return snapshot

    def action_view_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Snapshot'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
