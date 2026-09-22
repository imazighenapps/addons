from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestStockThreshold(models.Model):
    _name = 'pest.stock.threshold'
    _description = 'PestOps Stock Threshold'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'product_id, location_id'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.stock.threshold'),
        readonly=True,
        copy=False,
    )
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        tracking=True,
    )
    product_id = fields.Many2one(
        'product.product',
        required=True,
        ondelete='restrict',
        domain="[('type', '=', 'consu')]",
        tracking=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        required=True,
        ondelete='restrict',
        domain="[('usage', '=', 'internal')]",
        tracking=True,
    )
    minimum_qty = fields.Float(required=True, default=0.0, tracking=True)
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Alert Responsible',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    current_qty = fields.Float(compute='_compute_stock_status', string='Current Qty')
    shortage_qty = fields.Float(compute='_compute_stock_status', string='Shortage Qty')
    status = fields.Selection(
        [
            ('ok', 'OK'),
            ('low', 'Low Stock'),
            ('out', 'Out of Stock'),
        ],
        compute='_compute_stock_status',
        search='_search_status',
        string='Status',
    )
    alert_open = fields.Boolean(default=False, readonly=True, copy=False)
    last_alert_at = fields.Datetime(readonly=True, copy=False)
    last_alert_qty = fields.Float(readonly=True, copy=False)

    _sql_constraints = [
        (
            'product_location_company_unique',
            'unique(company_id, product_id, location_id)',
            'Only one active stock threshold is allowed per product and location.',
        ),
    ]

    @api.constrains('minimum_qty')
    def _check_minimum_qty(self):
        for record in self:
            if record.minimum_qty < 0:
                raise ValidationError(_('Minimum stock quantity cannot be negative.'))

    def _get_current_qty(self):
        self.ensure_one()
        if not self.product_id or not self.location_id:
            return 0.0
        return self.env['stock.quant']._get_available_quantity(
            self.product_id,
            self.location_id,
            strict=False,
        )

    def _compute_status_values(self):
        self.ensure_one()
        current = self._get_current_qty()
        if current <= 0:
            status = 'out'
        elif current <= self.minimum_qty:
            status = 'low'
        else:
            status = 'ok'
        shortage = max(self.minimum_qty - current, 0.0)
        return current, shortage, status

    @api.depends('product_id', 'location_id', 'minimum_qty', 'active')
    def _compute_stock_status(self):
        for record in self:
            if not record.active:
                record.current_qty = 0.0
                record.shortage_qty = 0.0
                record.status = 'ok'
                continue
            current, shortage, status = record._compute_status_values()
            record.current_qty = current
            record.shortage_qty = shortage
            record.status = status

    def _search_status(self, operator, value):
        if operator not in ('=', '!=', 'in', 'not in'):
            raise ValidationError(_('Unsupported search operator for stock status.'))
        values = list(value) if isinstance(value, (list, tuple)) else [value]
        matching = self.search([]).filtered(
            lambda record: record._compute_status_values()[2] in values
        )
        if operator in ('!=', 'not in'):
            return [('id', 'not in', matching.ids)]
        return [('id', 'in', matching.ids)]

    def _evaluate_and_alert(self):
        Activity = self.env['mail.activity'].sudo()
        todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not todo_type:
            return False
        for record in self.filtered('active'):
            current, shortage, status = record._compute_status_values()
            if status in ('low', 'out'):
                if not record.alert_open:
                    Activity.create({
                        'activity_type_id': todo_type.id,
                        'res_model_id': self.env['ir.model']._get_id('pest.stock.threshold'),
                        'res_id': record.id,
                        'user_id': record.responsible_user_id.id,
                        'summary': _('PestOps stock alert: %s') % record.product_id.display_name,
                        'note': _(
                            'Stock level is %s. Current quantity: %s %s; minimum: %s %s; location: %s.'
                        ) % (
                            dict(record._fields['status'].selection).get(status, status),
                            current,
                            record.product_id.uom_id.name,
                            record.minimum_qty,
                            record.product_id.uom_id.name,
                            record.location_id.display_name,
                        ),
                        'date_deadline': fields.Date.context_today(self),
                    })
                    record.sudo().write({
                        'alert_open': True,
                        'last_alert_at': fields.Datetime.now(),
                        'last_alert_qty': current,
                    })
            elif record.alert_open:
                record.sudo().write({'alert_open': False})
        return True

    @api.model
    def _cron_check_stock_thresholds(self):
        self.search([('active', '=', True)])._evaluate_and_alert()
        return True

    def action_check_now(self):
        self._evaluate_and_alert()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
