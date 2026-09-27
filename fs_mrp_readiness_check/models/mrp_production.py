from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fs_readiness_status = fields.Selection(
        [('ready', 'Ready'), ('warning', 'Warning'), ('blocked', 'Blocked')],
        compute='_compute_fs_readiness',
    )
    fs_readiness_blocker_count = fields.Integer(compute='_compute_fs_readiness')

    def _compute_fs_readiness(self):
        Check = self.env['fs.mrp.readiness.check']
        checks = Check.search([('production_id', 'in', self.ids)])
        mapping = {check.production_id.id: check for check in checks}
        for mo in self:
            check = mapping.get(mo.id)
            mo.fs_readiness_status = check.status if check else False
            mo.fs_readiness_blocker_count = check.blocker_count if check else 0

    def action_fs_check_readiness(self):
        self.ensure_one()
        check_model = self.env['fs.mrp.readiness.check']
        check = check_model.search([('production_id', '=', self.id)], limit=1)
        if not check:
            check = check_model.with_context(fs_mrp_readiness_internal=True).create({'production_id': self.id})
        check._run_check()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fs.mrp.readiness.check',
            'view_mode': 'form',
            'res_id': check.id,
            'target': 'new',
            'name': _('Readiness Check'),
        }

    def _fs_enforce_readiness(self):
        self.ensure_one()
        check_model = self.env['fs.mrp.readiness.check']
        check = check_model.search([('production_id', '=', self.id)], limit=1)
        if not check:
            check = check_model.with_context(fs_mrp_readiness_internal=True).create({'production_id': self.id})
        check._run_check()
        config = self.env['fs.mrp.readiness.config'].sudo().search(
            [('company_id', '=', self.company_id.id)], limit=1
        )
        if not config or config.blocking_policy == 'warn':
            return check
        if check.status == 'blocked':
            raise UserError(
                _(
                    'Production cannot start because the readiness check found %(count)s blocking issue(s). Review the readiness report first.',
                    count=check.blocker_count,
                )
            )
        return check

    def action_start(self):
        for production in self:
            production._fs_enforce_readiness()
        return super().action_start()
