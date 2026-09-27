from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


class BackorderControl(models.Model):
    _name = 'fs.backorder.control'
    _description = 'Backorder Control Analysis'
    _order = 'age_days desc, id desc'
    _check_company_auto = True
    _inherit = ['mail.activity.mixin']

    picking_id = fields.Many2one('stock.picking', required=True, index=True, ondelete='cascade')
    backorder_id = fields.Many2one(related='picking_id.backorder_id', store=True)
    company_id = fields.Many2one(related='picking_id.company_id', store=True, index=True)
    partner_id = fields.Many2one(related='picking_id.partner_id', store=True)
    warehouse_id = fields.Many2one(related='picking_id.picking_type_id.warehouse_id', store=True)
    state = fields.Selection(related='picking_id.state', store=True)
    age_days = fields.Integer(readonly=True, index=True)
    remaining_qty = fields.Float(readonly=True)
    product_count = fields.Integer(readonly=True)
    severity = fields.Selection(
        [('normal', 'Normal'), ('aging', 'Aging'), ('critical', 'Critical')],
        default='normal',
        required=True,
        index=True,
    )
    active = fields.Boolean(default=True, index=True)
    last_refreshed_at = fields.Datetime(readonly=True)

    _picking_unique = models.Constraint(
        'unique (picking_id)',
        'A picking can only appear once in the backorder control center.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_backorder_internal'):
            raise UserError(_('Backorder analysis rows are system-generated and cannot be created manually.'))
        return super().create(vals_list)

    def write(self, vals):
        if vals and not self.env.context.get('fs_backorder_internal'):
            raise UserError(_('Backorder analysis rows are system-generated and cannot be edited manually.'))
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get('fs_backorder_internal'):
            raise UserError(_('Backorder analysis rows are system-generated and cannot be deleted manually.'))
        return super().unlink()


    def action_open_picking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Backorder'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.picking_id.id,
        }

    def action_open_backorder_chain(self):
        self.ensure_one()
        chain = self.env['stock.picking']
        current = self.picking_id
        visited = set()
        while current and current.id not in visited:
            visited.add(current.id)
            chain |= current
            current = current.backorder_id
        pending = self.picking_id.backorder_ids
        while pending:
            next_pending = self.env['stock.picking']
            for picking in pending:
                if picking.id in visited:
                    continue
                visited.add(picking.id)
                chain |= picking
                next_pending |= picking.backorder_ids
            pending = next_pending
        return {
            'type': 'ir.actions.act_window',
            'name': _('Backorder Chain'),
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('id', 'in', chain.ids)],
            'context': {'create': False},
        }

    def action_schedule_review(self):
        if not self.env.user.has_group('stock.group_stock_user'):
            raise AccessError(_('Only inventory users can schedule backorder reviews.'))
        for rec in self.filtered(lambda record: record.active):
            user = rec.picking_id.user_id or self.env.user
            rec.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=user.id,
                summary=_('Review aged backorder'),
                note=_(
                    'Backorder %(picking)s has been open for %(days)s day(s) with %(qty)s remaining.',
                    picking=rec.picking_id.display_name,
                    days=rec.age_days,
                    qty=rec.remaining_qty,
                ),
            )
        return True

    def action_cancel_picking(self):
        """Cancel the linked open transfer using Odoo's native stock workflow."""
        if not self.env.user.has_group('stock.group_stock_manager'):
            raise AccessError(_('Only inventory managers can cancel a backorder from this screen.'))
        for rec in self:
            picking = rec.picking_id
            if picking.state in ('done', 'cancel'):
                raise UserError(
                    _('Backorder %(name)s can no longer be cancelled.', name=picking.display_name)
                )
            picking.action_cancel()
        return True

    @api.model
    def _refresh_record(self, rec, picking, now, config_by_company=None):
        config_by_company = config_by_company or {}
        config = config_by_company.get(picking.company_id.id)
        aging = config.aging_days if config else 7
        critical = config.critical_days if config else 30
        age_days = max((now - picking.create_date).days, 0) if picking.create_date else 0
        moves = picking.move_ids.filtered(lambda move: move.state not in ('done', 'cancel'))
        remaining = sum(
            max(move.product_uom_qty - move.quantity, 0.0)
            for move in moves
        )
        vals = {
            'age_days': age_days,
            'remaining_qty': remaining,
            'product_count': len(moves.mapped('product_id')),
            'severity': (
                'critical'
                if age_days >= critical
                else 'aging'
                if age_days >= aging
                else 'normal'
            ),
            'active': picking.state not in ('done', 'cancel') and remaining > 0,
            'last_refreshed_at': now,
        }
        if rec:
            rec.with_context(fs_backorder_internal=True).write(vals)
            return rec
        return self.with_context(fs_backorder_internal=True).create({'picking_id': picking.id, **vals})

    @api.model
    def cron_refresh(self, batch_size=500):
        """Refresh all backorders in deterministic batches and deactivate stale rows."""
        Pick = self.env['stock.picking']
        last_id = 0
        active_ids = set()
        while True:
            pickings = Pick.search(
                [
                    ('id', '>', last_id),
                    ('backorder_id', '!=', False),
                    ('state', 'not in', ('done', 'cancel')),
                ],
                order='id',
                limit=batch_size,
            )
            if not pickings:
                break
            config_by_company = {
                config.company_id.id: config
                for config in self.env['fs.backorder.control.config'].sudo().search(
                    [('company_id', 'in', pickings.company_id.ids)]
                )
            }
            existing = self.with_context(active_test=False).search([('picking_id', 'in', pickings.ids)])
            by_picking = {rec.picking_id.id: rec for rec in existing}
            now = fields.Datetime.now()
            for picking in pickings:
                rec = self._refresh_record(
                    by_picking.get(picking.id),
                    picking,
                    now,
                    config_by_company,
                )
                active_ids.add(rec.id)
            last_id = pickings[-1].id

        stale_domain = [('active', '=', True)]
        if active_ids:
            stale_domain.append(('id', 'not in', list(active_ids)))
        self.search(stale_domain).with_context(fs_backorder_internal=True).write({'active': False})
        return True
