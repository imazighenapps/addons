from odoo import _, http
from odoo.exceptions import AccessError, UserError
from odoo.http import request


class PurchaseVendorAckPortal(http.Controller):
    """Secure tokenized vendor acknowledgment endpoint."""

    def _get_ack(self, ack_id, token):
        ack = request.env['fs.purchase.vendor.ack'].sudo().browse(ack_id)
        if not ack.exists() or ack.access_token != token:
            return request.env['fs.purchase.vendor.ack']
        public_user = request.env.ref('base.public_user', raise_if_not_found=False)
        if public_user and request.env.user.id != public_user.id:
            user_partner = request.env.user.partner_id.commercial_partner_id
            vendor_partner = ack.vendor_id.commercial_partner_id
            if not user_partner or user_partner != vendor_partner:
                return request.env['fs.purchase.vendor.ack']
        return ack

    @http.route('/fs/vendor-ack/<int:ack_id>/<string:token>', type='http', auth='public', website=True, methods=['GET'], csrf=True)
    def display_ack(self, ack_id, token, **kwargs):
        ack = self._get_ack(ack_id, token)
        if not ack:
            return request.not_found()
        if not ack._is_token_valid():
            return request.render('fs_purchase_vendor_ack.portal_expired', {'ack': ack})
        return request.render('fs_purchase_vendor_ack.portal_ack_form', {'ack': ack})

    @http.route('/fs/vendor-ack/<int:ack_id>/<string:token>/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_ack(self, ack_id, token, **post):
        ack = self._get_ack(ack_id, token)
        if not ack:
            return request.not_found()
        try:
            ack.submit_from_portal(post)
        except (AccessError, UserError) as exc:
            return request.render('fs_purchase_vendor_ack.portal_error', {'message': str(exc)})
        return request.render('fs_purchase_vendor_ack.portal_success', {'ack': ack})
