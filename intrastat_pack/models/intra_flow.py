# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class IntraFlow(models.Model):
    _name = "intra.flow"
    _description = "Intrastat Flow Line"
    _order = "report_id, id"

    report_id = fields.Many2one(
        "intra.report", string="Declaration", required=True,
        ondelete="cascade", index=True)
    partner_country_id = fields.Many2one(
        "res.country", string="Partner Country", required=True,
        help="Member state of dispatch or arrival.")
    commodity_code = fields.Char(
        string="Commodity Code", required=True,
        help="Combined nomenclature code of the goods.")
    product_name = fields.Char(
        string="Goods Description", required=True,
        help="Short description of the goods moved.")
    quantity = fields.Float(default=1.0, required=True)
    value = fields.Float(
        string="Invoice Value", required=True,
        help="Statistical value of the movement in company currency.")
    weight = fields.Float(
        string="Net Mass (kg)", required=True,
        help="Net mass of the goods, excluding packaging.")
    company_id = fields.Many2one(
        related="report_id.company_id", store=True, readonly=True, index=True)

    @api.constrains("quantity", "value", "weight")
    def _check_amounts(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s must be above zero.",
                    line.product_name))
            if line.value < 0:
                raise ValidationError(_(
                    "The invoice value of %s cannot be negative.",
                    line.product_name))
            if line.weight <= 0:
                raise ValidationError(_(
                    "The net mass of %s must be above zero.",
                    line.product_name))

    @api.model_create_multi
    def create(self, vals_list):
        report_ids = {vals.get("report_id") for vals in vals_list
                      if vals.get("report_id")}
        if report_ids:
            filed = self.env["intra.report"].browse(list(report_ids)).filtered(
                lambda report: report.state == "filed")
            if filed:
                raise UserError(_(
                    "The filed declaration %s cannot receive new lines.",
                    filed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        if any(line.report_id.state == "filed" for line in self):
            raise UserError(_("A line on a filed declaration cannot be changed."))
        if vals.get("report_id"):
            target = self.env["intra.report"].browse(vals["report_id"])
            if target.state == "filed":
                raise UserError(_(
                    "The filed declaration %s cannot receive new lines.",
                    target.name))
        return super().write(vals)
