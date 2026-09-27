from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fs_cutoff_monitor_count = fields.Integer(compute='_compute_fs_cutoff_monitor_count')

    @api.depends('state', 'scheduled_date')
    def _compute_fs_cutoff_monitor_count(self):
        Monitor = self.env['fs.warehouse.cutoff.monitor']
        grouped = Monitor._read_group(
            [('picking_id', 'in', self.ids), ('status', '!=', 'completed')],
            ['picking_id'],
            ['__count'],
        )
        counts = {picking.id: count for picking, count in grouped}
        for picking in self:
            picking.fs_cutoff_monitor_count = counts.get(picking.id, 0)

    def action_fs_cutoff_monitor(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Warehouse Cut-off Monitor'),
            'res_model': 'fs.warehouse.cutoff.monitor',
            'view_mode': 'list,form',
            'domain': [('picking_id', '=', self.id)],
        }
