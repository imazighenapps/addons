# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request


class DocumentExpiryController(http.Controller):

    @http.route('/document_expiry/dashboard_data', type='json', auth='user')
    def dashboard_data(self):
        """Return JSON data for the OWL dashboard widget."""
        data = request.env['document.expiry'].get_dashboard_data()
        return data
