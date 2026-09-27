from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


class StockReservationAging(models.Model):
    _name = 'fs.stock.reservation.aging'
    _description = 'Stock Reservation Aging Analysis'
    _inherit = ['mail.thread']
    _order = 'age_days desc, id desc'
    _check_company_auto = True
    _rec_name = 'source_move_line_id'

    source_move_line_id = fields.Many2one(
        'stock.move.line',
        string='Reservation Line',
        index=True,
        ondelete='set null',
    )
    company_id = fields.Many2one('res.company', required=True, index=True, readonly=True)
    product_id = fields.Many2one('product.product', required=True, index=True, readonly=True)
    move_id = fields.Many2one('stock.move', index=True, readonly=True, ondelete='set null')
    picking_id = fields.Many2one('stock.picking', index=True, readonly=True, ondelete='set null')
    location_id = fields.Many2one('stock.location', index=True, readonly=True, ondelete='set null')
    sale_order_id = fields.Many2one('sale.order', index=True, readonly=True, ondelete='set null')
    reserved_quantity = fields.Float(readonly=True)
    reservation_since = fields.Datetime(readonly=True, index=True)
    reservation_date_approximate = fields.Boolean(default=True, readonly=True)
    age_days = fields.Integer(readonly=True, index=True)
    threshold_days = fields.Integer(readonly=True)
    critical_days = fields.Integer(readonly=True)
    bucket = fields.Selection(
        [
            ('normal', 'Normal'),
            ('aging', 'Aging'),
            ('critical', 'Critical'),
        ],
        default='normal',
        required=True,
        index=True,
    )
    state = fields.Selection(
        [('active', 'Active'), ('released', 'Released')],
        default='active',
        required=True,
        index=True,
        tracking=True,
    )
    released_at = fields.Datetime(readonly=True)
    released_by = fields.Many2one('res.users', readonly=True)
    release_reason = fields.Text(copy=False)
    last_refreshed_at = fields.Datetime(readonly=True)
    release_audit_ids = fields.One2many(
        'fs.stock.reservation.aging.release',
        'reservation_id',
        string='Release History',
        readonly=True,
    )

    _source_line_unique = models.Constraint(
        'unique (source_move_line_id)',
        'Each reserved move line can only have one analysis record.',
    )

    def _check_manager(self):
        if not self.env.user.has_group('stock.group_stock_manager'):
            raise AccessError(_('Only inventory managers can release reservations.'))

    @api.model
    def _prepare_from_move_line(self, line, *, reset_reservation=False):
        """Build a complete analysis snapshot from a native stock move line."""
        move = line.move_id
        sale_order = move.sale_line_id.order_id if move and move.sale_line_id else False
        now = fields.Datetime.now()
        return {
            'source_move_line_id': line.id,
            'company_id': line.company_id.id,
            'product_id': line.product_id.id,
            'move_id': move.id,
            'picking_id': line.picking_id.id,
            'location_id': line.location_id.id,
            'sale_order_id': sale_order.id,
            'reserved_quantity': line.quantity_product_uom,
            'reservation_since': now if reset_reservation else (line.create_date or now),
            'reservation_date_approximate': True,
            'age_days': 0,
            'state': 'active',
            'released_at': False,
            'released_by': False,
            'release_reason': False,
            'last_refreshed_at': now,
        }

    @api.model
    def _refresh_metrics(self, record, config=None):
        config = config or self.env['fs.stock.reservation.aging.config'].search(
            [('company_id', '=', record.company_id.id)], limit=1
        )
        aging_days = config.aging_days if config else 7
        critical_days = config.critical_days if config else 30
        now = fields.Datetime.now()
        age_days = max((now - record.reservation_since).days, 0) if record.reservation_since else 0
        bucket = (
            'critical' if age_days >= critical_days
            else 'aging' if age_days >= aging_days
            else 'normal'
        )
        record.with_context(fs_reservation_internal=True).write({
            'age_days': age_days,
            'threshold_days': aging_days,
            'critical_days': critical_days,
            'bucket': bucket,
            'last_refreshed_at': now,
        })

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_reservation_internal'):
            raise UserError(_('Reservation aging rows are system-generated and cannot be created manually.'))
        return super().create(vals_list)

    def write(self, vals):
        if vals and not self.env.context.get('fs_reservation_internal'):
            raise UserError(_('Reservation aging rows are system-generated and cannot be edited manually.'))
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get('fs_reservation_internal'):
            raise UserError(_('Reservation aging rows are historical analysis records and cannot be deleted manually.'))
        return super().unlink()


    def action_open_source(self):
        self.ensure_one()
        if not self.source_move_line_id:
            raise UserError(_('The original reservation line is no longer available.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reserved Move Line'),
            'res_model': 'stock.move.line',
            'view_mode': 'form',
            'res_id': self.source_move_line_id.id,
        }

    def action_open_release_wizard(self):
        self._check_manager()
        active = self.filtered(lambda r: r.state == 'active' and r.source_move_line_id)
        if not active:
            raise UserError(_('Select at least one active reservation.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Release Aging Reservations'),
            'res_model': 'fs.stock.reservation.release.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_reservation_ids': [(6, 0, active.ids)]},
        }

    def action_release(self, reason):
        """Safely release only the reserved quantity represented by each move line."""
        self._check_manager()
        reason = (reason or '').strip()
        if not reason:
            raise UserError(_('A release reason is required.'))
        for reservation in self.filtered(lambda r: r.state == 'active'):
            line = reservation.source_move_line_id
            if not line.exists() or not line.move_id:
                now = fields.Datetime.now()
                quantity = reservation.reserved_quantity
                reservation.with_context(fs_reservation_internal=True).write({
                    'state': 'released',
                    'released_at': now,
                    'released_by': self.env.user.id,
                    'release_reason': reason,
                    'age_days': 0,
                    'bucket': 'normal',
                })
                self.env['fs.stock.reservation.aging.release'].with_context(fs_reservation_internal=True).create({
                    'reservation_id': reservation.id,
                    'product_id': reservation.product_id.id,
                    'quantity': quantity,
                    'reason': reason,
                    'released_by': self.env.user.id,
                    'released_at': now,
                })
                continue
            if line.state in ('done', 'cancel') or line.move_id.state in ('done', 'cancel', 'draft'):
                raise UserError(
                    _('Reservation %(product)s can no longer be released because its stock move is no longer reservable.',
                      product=reservation.product_id.display_name)
                )
            quantity = line.quantity_product_uom
            if reservation.product_id.uom_id.is_zero(quantity):
                reservation.with_context(fs_reservation_internal=True).write({
                    'state': 'released',
                    'released_at': fields.Datetime.now(),
                    'released_by': self.env.user.id,
                    'release_reason': reason,
                })
                continue
            # Odoo 19's stock.move.line write() adjusts the reserved quants when the
            # reserved quantity is changed. This preserves the move and unreserves
            # only this specific line instead of unreserving the whole stock.move.
            line.write({'quantity': 0.0})
            now = fields.Datetime.now()
            reservation.with_context(fs_reservation_internal=True).write({
                'reserved_quantity': quantity,
                'state': 'released',
                'released_at': now,
                'released_by': self.env.user.id,
                'release_reason': reason,
                'age_days': 0,
                'bucket': 'normal',
            })
            self.env['fs.stock.reservation.aging.release'].with_context(fs_reservation_internal=True).create({
                'reservation_id': reservation.id,
                'move_line_id': line.id,
                'product_id': reservation.product_id.id,
                'quantity': quantity,
                'reason': reason,
                'released_by': self.env.user.id,
                'released_at': now,
            })
            reservation.message_post(
                body=_('Reservation released by %(user)s. Reason: %(reason)s',
                       user=self.env.user.display_name, reason=reason)
            )
        return True

    @api.model
    def refresh_analyses(self, batch_size=500):
        """Refresh active reservations in batches and keep released history."""
        MoveLine = self.env['stock.move.line']
        domain = [
            ('quantity_product_uom', '>', 0),
            ('picked', '=', False),
            ('move_id.state', 'not in', ('draft', 'done', 'cancel')),
        ]
        last_id = 0
        seen_ids = set()
        while True:
            lines = MoveLine.search(domain + [('id', '>', last_id)], limit=batch_size, order='id')
            if not lines:
                break
            last_id = lines[-1].id
            seen_ids.update(lines.ids)
            existing = self.search([('source_move_line_id', 'in', lines.ids)])
            by_line = {rec.source_move_line_id.id: rec for rec in existing if rec.source_move_line_id}
            config_by_company = {
                cfg.company_id.id: cfg
                for cfg in self.env['fs.stock.reservation.aging.config'].sudo().search([
                    ('company_id', 'in', lines.company_id.ids)
                ])
            }
            for line in lines:
                rec = by_line.get(line.id)
                if not rec:
                    rec = self.with_context(fs_reservation_internal=True).create(self._prepare_from_move_line(line))
                elif rec.state == 'released':
                    rec.with_context(fs_reservation_internal=True).write(self._prepare_from_move_line(line, reset_reservation=True))
                else:
                    rec.with_context(fs_reservation_internal=True).write({
                        'company_id': line.company_id.id,
                        'product_id': line.product_id.id,
                        'move_id': line.move_id.id,
                        'picking_id': line.picking_id.id,
                        'location_id': line.location_id.id,
                        'sale_order_id': line.move_id.sale_line_id.order_id.id if line.move_id.sale_line_id else False,
                        'reserved_quantity': line.quantity_product_uom,
                        'last_refreshed_at': fields.Datetime.now(),
                    })
                self._refresh_metrics(rec, config_by_company.get(line.company_id.id))

        active_records = self.search([('state', '=', 'active')], limit=1000)
        while active_records:
            for rec in active_records:
                if not rec.source_move_line_id.exists() or rec.source_move_line_id.id not in seen_ids:
                    rec.with_context(fs_reservation_internal=True).write({
                        'state': 'released',
                        'released_at': fields.Datetime.now(),
                        'released_by': self.env.user.id,
                        'release_reason': _('Reservation is no longer active in Odoo Stock.'),
                    })
            last = active_records[-1].id
            active_records = self.search([('state', '=', 'active'), ('id', '>', last)], limit=1000)
        return True

    @api.model
    def cron_refresh(self):
        return self.refresh_analyses()


class StockReservationAgingRelease(models.Model):
    _name = 'fs.stock.reservation.aging.release'
    _description = 'Stock Reservation Aging Release History'
    _order = 'released_at desc, id desc'
    _check_company_auto = True

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_reservation_internal'):
            raise UserError(_('Reservation release history is created by the release workflow.'))
        return super().create(vals_list)

    reservation_id = fields.Many2one(
        'fs.stock.reservation.aging', required=True, ondelete='cascade', index=True
    )
    move_line_id = fields.Many2one('stock.move.line', readonly=True, index=True, ondelete='set null')
    company_id = fields.Many2one(related='reservation_id.company_id', store=True, index=True)
    product_id = fields.Many2one('product.product', readonly=True)
    quantity = fields.Float(readonly=True)
    reason = fields.Text(required=True, readonly=True)
    released_by = fields.Many2one('res.users', required=True, readonly=True)
    released_at = fields.Datetime(required=True, readonly=True)
