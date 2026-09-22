from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestTreatment(models.Model):
    _inherit = 'pest.treatment'

    stock_trace_ids = fields.One2many(
        'pest.stock.trace',
        'treatment_id',
        string='Stock Traceability',
        readonly=True,
    )
    stock_trace_count = fields.Integer(compute='_compute_stock_trace_count')

    @api.depends('stock_trace_ids')
    def _compute_stock_trace_count(self):
        for treatment in self:
            treatment.stock_trace_count = len(treatment.stock_trace_ids)

    def _prevalidate_stock_consumption(self):
        StockQuant = self.env['stock.quant']
        now = fields.Datetime.now()
        for treatment in self:
            for line in treatment.line_ids.filtered(lambda l: l.consumption_state != 'done'):
                if not line.product_id:
                    raise ValidationError(_('Every consumption line must have a product.'))
                if line.quantity <= 0:
                    raise ValidationError(_('Consumed quantity must be greater than zero.'))
                source = line._get_source_location()
                if source.company_id and source.company_id != line.company_id:
                    raise UserError(_('The source location belongs to another company.'))
                tracking = getattr(line.product_id, 'tracking', 'none') or 'none'
                if tracking != 'none' and not line.lot_id:
                    raise ValidationError(_(
                        'Lot/serial tracking is enabled for %s. A lot/serial number is required.'
                    ) % line.product_id.display_name)
                if tracking == 'serial' and line.quantity > 1:
                    raise ValidationError(_(
                        'Serial-tracked product %s must be consumed one serial unit at a time.'
                    ) % line.product_id.display_name)
                if line.lot_id:
                    lot_product = line.lot_id.product_id
                    if lot_product and lot_product != line.product_id:
                        raise ValidationError(_('The selected lot does not belong to the selected product.'))
                    expiry = getattr(line.lot_id, 'life_date', False) or getattr(line.lot_id, 'expiration_date', False)
                    if expiry and expiry < now:
                        raise ValidationError(_(
                            'Lot %s is expired and cannot be consumed.'
                        ) % line.lot_id.display_name)
                available = 0.0
                if line.product_id.type == 'storable':
                    # Odoo only tracks quants for storable products; consumables
                    # and services are expensed on use, so no availability check.
                    available = StockQuant._get_available_quantity(
                        line.product_id,
                        source,
                        lot_id=line.lot_id,
                        strict=False,
                    )
                    if available + 1e-6 < line.quantity:
                        raise UserError(_(
                            'Insufficient stock for %s. Available: %s %s; requested: %s %s.'
                        ) % (
                            line.product_id.display_name,
                            available,
                            line.product_id.uom_id.name,
                            line.quantity,
                            line.product_id.uom_id.name,
                        ))

    def action_consume_products(self):
        self._prevalidate_stock_consumption()
        result = super().action_consume_products()
        for treatment in self:
            for line in treatment.line_ids.filtered(lambda l: l.consumption_state == 'done' and l.stock_move_id):
                line._ensure_stock_trace(line.stock_move_id)
        return result

    def action_view_stock_traces(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Traceability'),
            'res_model': 'pest.stock.trace',
            'view_mode': 'list,pivot,form',
            'domain': [('treatment_id', '=', self.id)],
            'context': {'default_treatment_id': self.id},
        }


class PestTreatmentLine(models.Model):
    _inherit = 'pest.treatment.line'

    trace_id = fields.Many2one(
        'pest.stock.trace',
        string='Trace',
        readonly=True,
        copy=False,
    )
    available_qty = fields.Float(compute='_compute_stock_indicators', string='Available Qty')
    stock_status = fields.Selection(
        [
            ('ok', 'Available'),
            ('low', 'Insufficient'),
            ('unknown', 'Unknown'),
        ],
        compute='_compute_stock_indicators',
        string='Stock Status',
    )
    lot_required = fields.Boolean(compute='_compute_stock_indicators')
    lot_expiration_date = fields.Datetime(compute='_compute_stock_indicators', string='Lot Expiration')

    @api.depends('product_id', 'location_id', 'lot_id', 'quantity', 'company_id')
    def _compute_stock_indicators(self):
        StockQuant = self.env['stock.quant']
        for line in self:
            tracking = getattr(line.product_id, 'tracking', 'none') if line.product_id else 'none'
            line.lot_required = bool(line.product_id and tracking != 'none')
            expiry = False
            if line.lot_id:
                expiry = getattr(line.lot_id, 'life_date', False) or getattr(line.lot_id, 'expiration_date', False)
            line.lot_expiration_date = expiry
            line.available_qty = 0.0
            line.stock_status = 'unknown'
            if not line.product_id:
                continue
            try:
                source = line._get_source_location()
                available = StockQuant._get_available_quantity(
                    line.product_id,
                    source,
                    lot_id=line.lot_id,
                    strict=False,
                )
                line.available_qty = available
                line.stock_status = 'ok' if available + 1e-6 >= line.quantity else 'low'
            except Exception:
                line.stock_status = 'unknown'

    def _ensure_stock_trace(self, move):
        self.ensure_one()
        if not move:
            return False
        Trace = self.env['pest.stock.trace'].sudo()
        trace = self.trace_id or Trace.search([('stock_move_id', '=', move.id)], limit=1)
        if trace:
            if not self.trace_id:
                self.sudo().write({'trace_id': trace.id})
            return trace
        treatment = self.treatment_id
        visit = treatment.visit_id
        lot_expiration = False
        if self.lot_id:
            lot_expiration = getattr(self.lot_id, 'life_date', False) or getattr(self.lot_id, 'expiration_date', False)
        vals = {
            'consumed_at': treatment.date or fields.Datetime.now(),
            'company_id': treatment.company_id.id,
            'technician_id': treatment.technician_id.id,
            'treatment_id': treatment.id,
            'treatment_line_id': self.id,
            'visit_id': visit.id,
            'site_id': treatment.site_id.id,
            'zone_id': treatment.zone_id.id,
            'product_id': self.product_id.id,
            'lot_id': self.lot_id.id,
            'source_location_id': move.location_id.id,
            'destination_location_id': move.location_dest_id.id,
            'stock_move_id': move.id,
            'quantity': self.quantity,
            'uom_id': self.uom_id.id,
            'lot_expiration_date': lot_expiration,
            'notes': self.notes,
        }
        trace = Trace.create(vals)
        self.sudo().write({'trace_id': trace.id})
        return trace

    def action_view_trace(self):
        self.ensure_one()
        if not self.trace_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Consumption Trace'),
            'res_model': 'pest.stock.trace',
            'view_mode': 'form',
            'res_id': self.trace_id.id,
            'target': 'current',
        }
