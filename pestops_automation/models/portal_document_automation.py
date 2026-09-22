from odoo import fields, models


class PestPortalDocumentAutomation(models.Model):
    _inherit = 'pest.portal.document'

    published_at = fields.Datetime(readonly=True, copy=False)

    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.published:
                record.published_at = fields.Datetime.now()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'published' in vals:
            for record in self:
                record.published_at = fields.Datetime.now() if record.published else False
        return res
