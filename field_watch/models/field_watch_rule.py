# -*- coding: utf-8 -*-
from odoo import fields, models


class FieldWatchRule(models.Model):
    _name = "field.watch.rule"
    _description = "Field Watch Rule"

    name = fields.Char(required=True)
    model_id = fields.Many2one(
        "ir.model", string="Model", required=True, ondelete="cascade")
    field_names = fields.Text(
        help="One technical field name per line. Leave empty to watch every "
             "tracked field of the model.")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    note = fields.Text()

    def _matches(self, model_name, field_name):
        self.ensure_one()
        if self.model_id.model != model_name:
            return False
        names = [name.strip() for name in (self.field_names or "").splitlines()
                 if name.strip()]
        return not names or field_name in names
