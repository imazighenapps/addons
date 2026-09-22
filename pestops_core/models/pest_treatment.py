from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestTreatment(models.Model):
    _name = 'pest.treatment'
    _description = 'Pest Treatment'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.treatment'),
        readonly=True,
        copy=False,
    )
    visit_id = fields.Many2one(
        'pest.visit',
        required=True,
        ondelete='cascade',
        index=True,
    )
    site_id = fields.Many2one(
        related='visit_id.site_id',
        store=True,
        index=True,
    )
    zone_id = fields.Many2one('pest.zone', ondelete='restrict')
    pest_id = fields.Many2one('pest.type', ondelete='restrict')
    method_id = fields.Many2one('pest.treatment.method', ondelete='restrict')

    technician_id = fields.Many2one(
        related='visit_id.technician_id',
        store=True,
    )
    company_id = fields.Many2one(
        related='visit_id.company_id',
        store=True,
        index=True,
    )
    date = fields.Datetime(default=fields.Datetime.now, required=True)

    result = fields.Selection(
        [
            ('completed', 'Completed'),
            ('partial', 'Partial'),
            ('follow_up', 'Follow-up Required'),
        ],
        default='completed',
        required=True,
    )
    instructions = fields.Html()
    notes = fields.Text()
    image_1920 = fields.Image()

    line_ids = fields.One2many(
        'pest.treatment.line',
        'treatment_id',
        copy=True,
    )

    stock_consumption_state = fields.Selection(
        [
            ('none', 'Not Consumed'),
            ('partial', 'Partially Consumed'),
            ('done', 'Consumed'),
        ],
        compute='_compute_stock_consumption_state',
        store=True,
    )

    @api.depends('line_ids.consumption_state')
    def _compute_stock_consumption_state(self):
        for treatment in self:
            lines = treatment.line_ids
            if not lines:
                treatment.stock_consumption_state = 'none'
            elif all(line.consumption_state == 'done' for line in lines):
                treatment.stock_consumption_state = 'done'
            elif any(line.consumption_state == 'done' for line in lines):
                treatment.stock_consumption_state = 'partial'
            else:
                treatment.stock_consumption_state = 'none'

    def action_consume_products(self):
        StockMove = self.env['stock.move']
        for treatment in self:
            for line in treatment.line_ids.filtered(lambda l: l.consumption_state != 'done'):
                if not line.product_id:
                    continue
                if line.quantity <= 0:
                    raise ValidationError(_('Consumed quantity must be greater than zero.'))
                move = line._create_done_stock_move()
                line.stock_move_id = move.id
                line.consumption_state = 'done'
        return True


class PestTreatmentLine(models.Model):
    _name = 'pest.treatment.line'
    _description = 'Pest Treatment Consumption'

    treatment_id = fields.Many2one(
        'pest.treatment',
        required=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        related='treatment_id.company_id',
        store=True,
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        required=True,
        ondelete='restrict',
        domain="[('type', '=', 'consu')]",
    )
    lot_id = fields.Many2one(
        'stock.lot',
        ondelete='restrict',
        domain="[('product_id', '=', product_id)]",
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        ondelete='restrict',
        domain="[('usage', '=', 'internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    planned_quantity = fields.Float(string='Planned Quantity', default=0.0)
    quantity = fields.Float(string='Actual Quantity', required=True, default=1.0)
    quantity_variance = fields.Float(compute='_compute_quantity_variance', store=True)
    uom_id = fields.Many2one(
        'uom.uom',
        related='product_id.uom_id',
        readonly=True,
    )
    notes = fields.Char()

    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        readonly=True,
        copy=False,
    )
    consumption_state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('done', 'Done'),
        ],
        default='pending',
        readonly=True,
        copy=False,
    )

    @api.depends('planned_quantity', 'quantity')
    def _compute_quantity_variance(self):
        for line in self:
            line.quantity_variance = line.quantity - line.planned_quantity if line.planned_quantity else 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.location_id:
            warehouse = self.env['stock.warehouse'].search([
                ('company_id', '=', self.company_id.id or self.env.company.id),
            ], limit=1)
            self.location_id = warehouse.lot_stock_id if warehouse else False

    @api.constrains('lot_id', 'product_id')
    def _check_lot_product(self):
        for line in self:
            if line.lot_id and line.product_id != line.lot_id.product_id:
                raise ValidationError(_('The selected lot does not belong to the selected product.'))

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Consumption quantity must be greater than zero.'))

    def _get_source_location(self):
        self.ensure_one()
        if self.location_id:
            return self.location_id
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        if warehouse:
            return warehouse.lot_stock_id
        raise UserError(_('Please configure a source stock location for product consumption.'))

    def _get_destination_location(self):
        self.ensure_one()
        # Odoo 19 no longer ships the stock.stock_location_inventory XMLID;
        # the virtual "Inventory adjustment" location (usage='inventory')
        # is created by post-init hooks instead.
        location = self.env['stock.location'].search(
            [('usage', '=', 'inventory')],
            order='company_id, id',
            limit=1,
        )
        if not location:
            raise UserError(_('No inventory adjustment location could be found.'))
        return location

    def _create_done_stock_move(self):
        self.ensure_one()

        if self.stock_move_id and self.stock_move_id.state == 'done':
            return self.stock_move_id

        source = self._get_source_location()
        destination = self._get_destination_location()

        if source.company_id and source.company_id != self.company_id:
            raise UserError(_('The source location belongs to another company.'))

        # Odoo only tracks quants for storable products; consumables and
        # services are expensed on use, so the availability check applies
        # to storable products only.
        if self.product_id.type == 'storable':
            available = self.env['stock.quant']._get_available_quantity(
                self.product_id, source, lot_id=self.lot_id, strict=False
            )
            if available + 1e-6 < self.quantity:
                raise UserError(_(
                    'Insufficient stock for %s. Available: %s %s; requested: %s %s.'
                ) % (self.product_id.display_name, available, self.product_id.uom_id.name, self.quantity, self.product_id.uom_id.name))

        Move = self.env['stock.move']
        move = Move.create({
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_id.uom_id.id,
            'location_id': source.id,
            'location_dest_id': destination.id,
            'company_id': self.company_id.id,
            'date': self.treatment_id.date or fields.Datetime.now(),
            'origin': f'PestOps Treatment {self.treatment_id.name}',
            'picked': True,
            'is_inventory': False,
        })

        move._action_confirm(merge=False, create_proc=False)

        move_line_vals = {
            'move_id': move.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'quantity': self.quantity,
            'location_id': source.id,
            'location_dest_id': destination.id,
            'picked': True,
        }
        if self.lot_id:
            move_line_vals['lot_id'] = self.lot_id.id

        self.env['stock.move.line'].create(move_line_vals)

        move._action_done(cancel_backorder=True)
        return move
