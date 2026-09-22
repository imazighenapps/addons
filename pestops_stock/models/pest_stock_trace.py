from odoo import fields, models, _


class PestStockTrace(models.Model):
    _name = 'pest.stock.trace'
    _description = 'PestOps Stock Consumption Trace'
    _inherit = ['mail.thread']
    _order = 'consumed_at desc, id desc'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.stock.trace'),
        readonly=True,
        copy=False,
    )
    consumed_at = fields.Datetime(default=fields.Datetime.now, readonly=True, index=True)
    company_id = fields.Many2one('res.company', readonly=True, index=True)
    technician_id = fields.Many2one('res.users', readonly=True, index=True)
    treatment_id = fields.Many2one('pest.treatment', readonly=True, ondelete='restrict', index=True)
    treatment_line_id = fields.Many2one('pest.treatment.line', readonly=True, ondelete='restrict', index=True)
    visit_id = fields.Many2one('pest.visit', readonly=True, ondelete='restrict', index=True)
    site_id = fields.Many2one('pest.site', readonly=True, ondelete='restrict', index=True)
    zone_id = fields.Many2one('pest.zone', readonly=True, ondelete='restrict', index=True)
    product_id = fields.Many2one('product.product', readonly=True, ondelete='restrict', index=True)
    lot_id = fields.Many2one('stock.lot', readonly=True, ondelete='restrict', index=True)
    source_location_id = fields.Many2one('stock.location', readonly=True, ondelete='restrict')
    destination_location_id = fields.Many2one('stock.location', readonly=True, ondelete='restrict')
    stock_move_id = fields.Many2one('stock.move', readonly=True, ondelete='restrict', index=True)
    quantity = fields.Float(readonly=True)
    uom_id = fields.Many2one('uom.uom', readonly=True, ondelete='restrict')
    lot_expiration_date = fields.Datetime(readonly=True)
    notes = fields.Char(readonly=True)

    _sql_constraints = [
        (
            'stock_move_unique',
            'unique(stock_move_id)',
            'A stock move can only be linked to one PestOps consumption trace.',
        ),
    ]

    def action_view_stock_move(self):
        self.ensure_one()
        if not self.stock_move_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Move'),
            'res_model': 'stock.move',
            'view_mode': 'form',
            'res_id': self.stock_move_id.id,
            'target': 'current',
        }

    def action_view_treatment(self):
        self.ensure_one()
        if not self.treatment_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Treatment'),
            'res_model': 'pest.treatment',
            'view_mode': 'form',
            'res_id': self.treatment_id.id,
            'target': 'current',
        }
