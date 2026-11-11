# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RecodeLine(models.Model):
    _name = "recode.line"
    _description = "Recode Reference Line"
    _order = "request_id, id"

    request_id = fields.Many2one(
        "recode.request", required=True, ondelete="cascade", index=True)
    source = fields.Char(required=True, help="Where this reference lives.")
    old_value = fields.Char(required=True)
    new_value = fields.Char()
    updated = fields.Boolean(default=False)
    company_id = fields.Many2one(
        related="request_id.company_id", store=True, readonly=True)

    @api.constrains("old_value", "new_value")
    def _check_values(self):
        for line in self:
            if line.new_value and line.new_value == line.old_value:
                raise ValidationError(_(
                    "The new value of %s must differ from the old value.",
                    line.source))

    @api.model_create_multi
    def create(self, vals_list):
        requests = self.env["recode.request"].browse(
            [v.get("request_id") for v in vals_list if v.get("request_id")])
        for req in requests:
            if req.state == "done":
                raise UserError(_(
                    "Cannot add references to an applied request."))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.request_id.state == "done" and set(vals) - {"updated", "new_value"}:
                raise UserError(_(
                    "References of an applied request cannot be changed."))
        return super().write(vals)
