from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fs_picking_exception_count = fields.Integer(compute='_compute_fs_picking_exception_count')

    @api.depends('state')
    def _compute_fs_picking_exception_count(self):
        Exception = self.env['fs.picking.exception']
        grouped = Exception._read_group(
            [('picking_id', 'in', self.ids), ('state', '=', 'open')],
            ['picking_id'],
            ['__count'],
        )
        counts = {picking.id: count for picking, count in grouped}
        for picking in self:
            picking.fs_picking_exception_count = counts.get(picking.id, 0)

    def action_fs_picking_exceptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Picking Exceptions'),
            'res_model': 'fs.picking.exception',
            'view_mode': 'list,form',
            'domain': [('picking_id', '=', self.id), ('state', '=', 'open')],
        }
