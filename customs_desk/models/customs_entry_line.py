# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CustomsEntryLine(models.Model):
    _name = "customs.entry.line"
    _description = "Customs Entry Line"
    _order = "entry_id, id"

    entry_id = fields.Many2one(
        "customs.entry", string="Customs Entry", required=True,
        ondelete="cascade", index=True)
    duty_code_id = fields.Many2one(
        "customs.duty.code", string="HS Code", required=True)
    duty_rate = fields.Float(
        related="duty_code_id.duty_rate", store=True, readonly=True)
    description = fields.Char(required=True)
    quantity = fields.Float(default=1.0, required=True)
    customs_value = fields.Monetary(
        required=True, currency_field="currency_id",
        help="Declared customs value of this line.")
    duty_amount = fields.Monetary(
        compute="_compute_duty_amount", store=True, currency_field="currency_id",
        help="Duty computed from the customs value and the HS code rate.")
    currency_id = fields.Many2one(
        related="entry_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="entry_id.company_id", store=True, readonly=True, index=True)

    @api.depends("customs_value", "duty_rate")
    def _compute_duty_amount(self):
        for line in self:
            line.duty_amount = line.customs_value * (line.duty_rate or 0.0) / 100.0

    @api.constrains("quantity", "customs_value")
    def _check_values(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s must be above zero.", line.description))
            if line.customs_value < 0:
                raise ValidationError(_(
                    "The customs value of %s cannot be negative.",
                    line.description))

    @api.model_create_multi
    def create(self, vals_list):
        entry_ids = {vals.get("entry_id") for vals in vals_list
                     if vals.get("entry_id")}
        if entry_ids:
            cleared = self.env["customs.entry"].browse(list(entry_ids)).filtered(
                lambda entry: entry.state == "cleared")
            if cleared:
                raise UserError(_(
                    "The cleared entry %s cannot receive new lines.",
                    cleared[0].name))
        return super().create(vals_list)

    def write(self, vals):
        if any(line.entry_id.state == "cleared" for line in self):
            raise UserError(_("A line on a cleared entry cannot be changed."))
        if vals.get("entry_id"):
            target = self.env["customs.entry"].browse(vals["entry_id"])
            if target.state == "cleared":
                raise UserError(_(
                    "The cleared entry %s cannot receive new lines.",
                    target.name))
        return super().write(vals)
