from odoo import api, models


class PestServiceRequestAutomation(models.Model):
    _inherit = 'pest.service.request'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # The scheduled automation engine handles activities and optional customer email.
        return records
