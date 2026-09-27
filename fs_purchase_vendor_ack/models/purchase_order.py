from odoo import _, fields, models
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fs_vendor_ack_count = fields.Integer(compute='_compute_fs_vendor_ack_count')

    def _compute_fs_vendor_ack_count(self):
        Ack = self.env['fs.purchase.vendor.ack']
        data = Ack._read_group(
            [('purchase_order_id', 'in', self.ids)],
            ['purchase_order_id'],
            ['__count'],
        )
        counts = {po.id: count for po, count in data}
        for order in self:
            order.fs_vendor_ack_count = counts.get(order.id, 0)

    def _invalidate_fs_vendor_acknowledgments(self):
        """Invalidate affected acknowledgments and version submitted responses after PO changes.

        Draft/sent requests become historical. A submitted/contested response is also historical,
        but the current PO state needs a fresh draft snapshot so that the supplier cannot answer
        against obsolete quantities or dates.
        """
        Ack = self.env['fs.purchase.vendor.ack']
        for order in self:
            active = Ack.search([
                ('purchase_order_id', '=', order.id),
                ('state', 'in', ('draft', 'sent', 'submitted', 'contested')),
            ], order='version desc')
            if not active:
                continue
            needs_new_version = active[0].state in ('submitted', 'contested')
            active.with_context(fs_vendor_ack_transition=True).write({'state': 'superseded'})
            if needs_new_version and order.state != 'cancel':
                Ack.with_context(fs_vendor_ack_system_change=True).create_from_purchase_order(order)

    def write(self, vals):
        result = super().write(vals)
        if (
            not self.env.context.get('fs_vendor_ack_skip_invalidation')
            and self.env['fs.purchase.vendor.ack']._material_purchase_change(vals)
        ):
            self._invalidate_fs_vendor_acknowledgments()
        return result

    def action_fs_create_vendor_ack(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase.group_purchase_user'):
            raise AccessError(_('Only purchase users can manage supplier acknowledgments.'))
        ack = self.env['fs.purchase.vendor.ack'].create_from_purchase_order(self)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fs.purchase.vendor.ack',
            'view_mode': 'form',
            'res_id': ack.id,
            'target': 'current',
            'name': _('Vendor Acknowledgment'),
        }

    def action_fs_open_vendor_ack(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase.group_purchase_user'):
            raise AccessError(_('Only purchase users can view supplier acknowledgments.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fs.purchase.vendor.ack',
            'view_mode': 'list,form',
            'domain': [('purchase_order_id', '=', self.id)],
            'name': _('Vendor Acknowledgments'),
        }
