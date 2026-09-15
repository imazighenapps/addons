from odoo import fields, models, _


class GuardianSnapshotWizard(models.TransientModel):
    _name = 'fs.guardian.snapshot.wizard'
    _description = 'Create and Compare Guardian Snapshot'

    baseline_id = fields.Many2one('fs.guardian.baseline', required=True)

    def action_create_and_compare(self):
        self.ensure_one()
        snapshot = self.env['fs.guardian.snapshot'].create_from_current(self.baseline_id, is_baseline=False)
        from ..services.diff_service import GuardianDiffService
        baseline_snapshot = self.baseline_id.snapshot_id
        changes = GuardianDiffService(self.env).compare(baseline_snapshot, snapshot)
        Change = self.env['fs.guardian.change']
        created = Change.browse()
        for change in changes:
            created |= Change.create_change(self.baseline_id, change['item'], change['before'], change['after'], change['operation'], change['risk'])
        self.baseline_id.message_post(body=_('%s configuration changes detected in %s.') % (len(created), snapshot.display_name))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Detected Configuration Changes'),
            'res_model': 'fs.guardian.change',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created.ids)],
        }
