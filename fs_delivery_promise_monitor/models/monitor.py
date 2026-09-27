from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DeliveryPromiseRisk(models.Model):
    _name = 'fs.delivery.promise.risk'
    _description = 'Delivery Promise Risk'
    _order = 'commitment_date asc, id desc'
    _check_company_auto = True

    sale_order_id = fields.Many2one('sale.order', required=True, index=True, ondelete='cascade')
    company_id = fields.Many2one(related='sale_order_id.company_id', store=True, index=True)
    partner_id = fields.Many2one(related='sale_order_id.partner_id', store=True)
    user_id = fields.Many2one(related='sale_order_id.user_id', store=True)
    commitment_date = fields.Datetime(related='sale_order_id.commitment_date', store=True, index=True)
    expected_date = fields.Datetime(related='sale_order_id.expected_date', store=True)
    latest_scheduled_date = fields.Datetime(readonly=True)
    actual_delivery_date = fields.Datetime(readonly=True)
    status = fields.Selection(
        [
            ('safe', 'Safe'),
            ('at_risk', 'At Risk'),
            ('late', 'Late'),
            ('delivered_late', 'Delivered Late'),
        ],
        required=True,
        index=True,
    )
    risk_days = fields.Float(readonly=True)
    reason = fields.Text(readonly=True)
    open = fields.Boolean(default=True, index=True)
    last_checked_at = fields.Datetime(readonly=True)

    _sale_order_unique = models.Constraint(
        'unique (sale_order_id)',
        'Only one delivery risk record is allowed per sales order.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_delivery_promise_internal'):
            raise UserError(_('Delivery promise risk rows are system-generated and cannot be created manually.'))
        return super().create(vals_list)

    def write(self, vals):
        if vals and not self.env.context.get('fs_delivery_promise_internal'):
            raise UserError(_('Delivery promise risk rows are system-generated and cannot be edited manually.'))
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get('fs_delivery_promise_internal'):
            raise UserError(_('Delivery promise risk rows are system-generated and cannot be deleted manually.'))
        return super().unlink()


    def action_open_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'name': _('Sales Order'),
        }

    def action_refresh(self):
        self.ensure_one()
        self.refresh(self.sale_order_id)
        return True

    @api.model
    def _evaluate_order(self, order, config=None):
        """Evaluate the customer promise against the current outgoing logistics plan."""
        promise = order.commitment_date
        if not promise:
            return None

        pickings = order.picking_ids.filtered(
            lambda picking: picking.state != 'cancel' and picking.picking_type_code == 'outgoing'
        )
        open_pickings = pickings.filtered(lambda picking: picking.state != 'done')
        done_pickings = pickings.filtered(lambda picking: picking.state == 'done')
        now = fields.Datetime.now()
        actual = max(done_pickings.mapped('date_done'), default=False)
        scheduled = max(open_pickings.mapped('scheduled_date'), default=False)

        if not open_pickings and actual:
            late = actual > promise
            return {
                'status': 'delivered_late' if late else 'safe',
                'risk_days': max((actual - promise).total_seconds() / 86400.0, 0.0) if late else 0.0,
                'reason': (
                    _('Delivered after the customer promise.')
                    if late
                    else _('Delivered on or before the customer promise.')
                ),
                'latest_scheduled_date': scheduled,
                'actual_delivery_date': actual,
                'open': False,
            }

        warning_hours = config.warning_hours if config else 24.0

        if scheduled and scheduled > promise:
            return {
                'status': 'late',
                'risk_days': (scheduled - promise).total_seconds() / 86400.0,
                'reason': _('The latest open transfer schedule is later than the customer promise.'),
                'latest_scheduled_date': scheduled,
                'actual_delivery_date': actual,
                'open': True,
            }

        hours = (promise - now).total_seconds() / 3600.0
        if hours < 0:
            status = 'late'
            risk_days = abs(hours) / 24.0
            reason = _('The customer promise has already passed while delivery remains open.')
        elif hours <= warning_hours:
            status = 'at_risk'
            risk_days = max((warning_hours - hours) / 24.0, 0.0)
            reason = _('The promise is approaching the configured warning window.')
        else:
            status = 'safe'
            risk_days = 0.0
            reason = _('Current logistics scheduling remains compatible with the customer promise.')

        return {
            'status': status,
            'risk_days': risk_days,
            'reason': reason,
            'latest_scheduled_date': scheduled,
            'actual_delivery_date': actual,
            'open': True,
        }

    @api.model
    def refresh(self, orders=None):
        """Refresh the monitor for the supplied sale orders, or all relevant orders."""
        Sale = self.env['sale.order']
        if orders is None or not orders:
            orders = Sale.search(
                [('state', 'in', ('sale', 'done')), ('commitment_date', '!=', False)],
                order='id',
            )
        else:
            orders = orders.filtered(lambda order: order.state in ('sale', 'done') and order.commitment_date)

        if not orders:
            return True

        now = fields.Datetime.now()
        existing = self.search([('sale_order_id', 'in', orders.ids)])
        by_order = {rec.sale_order_id.id: rec for rec in existing}
        config_by_company = {
            cfg.company_id.id: cfg
            for cfg in self.env['fs.delivery.promise.monitor.config'].sudo().search(
                [('company_id', 'in', orders.company_id.ids)]
            )
        }

        for order in orders:
            vals = self._evaluate_order(order, config_by_company.get(order.company_id.id))
            if not vals:
                continue
            previous = by_order.get(order.id).status if by_order.get(order.id) else False
            vals.update({'sale_order_id': order.id, 'last_checked_at': now})
            rec = by_order.get(order.id)
            if rec:
                rec.with_context(fs_delivery_promise_internal=True).write(vals)
            else:
                rec = self.with_context(fs_delivery_promise_internal=True).create(vals)

            config = config_by_company.get(order.company_id.id)
            if (
                config
                and config.notification_mode == 'activity'
                and previous != rec.status
                and rec.status in ('at_risk', 'late', 'delivered_late')
            ):
                order.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_(
                        'Delivery promise status: %(status)s',
                        status=rec.status.replace('_', ' ').title(),
                    ),
                    note=rec.reason,
                )
        return True

    @api.model
    def cron_refresh(self, batch_size=500):
        """Process all matching orders in deterministic batches to avoid long cron transactions."""
        Sale = self.env['sale.order']
        last_id = 0
        while True:
            orders = Sale.search(
                [
                    ('id', '>', last_id),
                    ('state', 'in', ('sale', 'done')),
                    ('commitment_date', '!=', False),
                ],
                order='id',
                limit=batch_size,
            )
            if not orders:
                break
            self.refresh(orders)
            last_id = orders[-1].id
        return True
