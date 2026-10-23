# -*- coding: utf-8 -*-
from odoo import api, fields, models
from .rep_material import ECO_ORGS


class ResCompany(models.Model):
    _inherit = "res.company"

    rep_eco_org = fields.Selection(ECO_ORGS, string="Default REP Eco-organism", default="citeo")
    rep_auto_ledger = fields.Boolean(string="Auto-create REP lines on delivery")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rep_packaging_ids = fields.Many2many(
        "rep.packaging", "product_template_rep_packaging_rel",
        "product_template_id", "rep_packaging_id",
        string="REP Packaging")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rep_eco_estimate = fields.Float(
        string="REP Estimate (€)", compute="_compute_rep_estimate")

    @api.depends("product_id", "product_uom_qty")
    def _compute_rep_estimate(self):
        for line in self:
            total = 0.0
            if line.product_id:
                pkgs = self.env["rep.packaging"].search(
                    [("product_ids", "in", line.product_id.product_tmpl_id.ids)])
                eco = line.company_id.rep_eco_org or "citeo"
                for pkg in pkgs:
                    total += pkg._eco_cost_for_qty(line.product_uom_qty, eco_org=eco)
            line.rep_eco_estimate = round(total, 4)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    rep_ledger_done = fields.Boolean(copy=False)

    def action_rep_generate(self):
        for picking in self.filtered(lambda p: p.state == "done" and not p.rep_ledger_done):
            for move in picking.move_ids:
                tmpl = move.product_id.product_tmpl_id
                pkgs = self.env["rep.packaging"].search([("product_ids", "in", tmpl.ids)])
                eco = picking.company_id.rep_eco_org or "citeo"
                for pkg in pkgs:
                    qty_units = move.quantity or 0.0
                    tariff = pkg._tariff(eco, 2026)
                    self.env["rep.ledger"].create({
                        "date": fields.Date.today(),
                        "company_id": picking.company_id.id,
                        "country_id": picking.partner_id.country_id.id or False,
                        "packaging_id": pkg.id,
                        "weight_kg": pkg.weight_g * pkg.qty_per_unit * qty_units / 1000.0,
                        "tariff_id": tariff.id if tariff else False,
                        "amount": pkg._eco_cost_for_qty(qty_units, eco_org=eco),
                        "source": "delivery",
                        "origin": picking.name,
                    })
            picking.rep_ledger_done = True
        return True
