from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound


class PestOpsController(http.Controller):

    @http.route(
        '/pestops/scan/<string:token>',
        type='http',
        auth='user',
        methods=['GET'],
    )
    def pestops_scan(self, token, **kwargs):
        point = request.env['pest.control.point'].search(
            [('qr_token', '=', token), ('active', '=', True)],
            limit=1,
        )
        if not point:
            raise NotFound('PestOps control point not found.')

        return request.redirect(
            f'/web#id={point.id}&model=pest.control.point&view_type=form'
        )
