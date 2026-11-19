# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request


class DocumentExpiryController(http.Controller):

    @http.route('/document_expiry/dashboard_data', type='jsonrpc', auth='user')
    def dashboard_data(self):
        """Return JSON data for the OWL dashboard widget."""
        return request.env['document.expiry'].sudo(False).get_dashboard_data()
