from odoo import _, fields, models
from odoo.exceptions import AccessError, UserError


class StockReservationReleaseWizard(models.TransientModel):
    _name = 'fs.stock.reservation.release.wizard'
    _description = 'Release Aging Stock Reservations'

    reservation_ids = fields.Many2many(
        'fs.stock.reservation.aging',
        relation='fs_reservation_release_rel',
        required=True,
    )
    reason = fields.Text(required=True)

    def action_release(self):
        self.ensure_one()
        if not self.env.user.has_group('stock.group_stock_manager'):
            raise AccessError(_('Only inventory managers can release reservations.'))
        if not self.reason or not self.reason.strip():
            raise UserError(_('A release reason is required.'))
        self.reservation_ids.action_release(self.reason.strip())
        return {'type': 'ir.actions.client', 'tag': 'reload'}
