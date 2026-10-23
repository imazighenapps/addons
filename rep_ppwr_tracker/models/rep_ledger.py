# -*- coding: utf-8 -*-
from odoo import api, fields, models
from .rep_material import ECO_ORGS


class RepLedger(models.Model):
    _name = "rep.ledger"
    _description = "REP Packaging Ledger (placed on market)"
    _order = "date desc"

    name = fields.Char(default="/", copy=False)
    date = fields.Date(default=fields.Date.today, required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    country_id = fields.Many2one("res.country", string="Destination Country")
    packaging_id = fields.Many2one("rep.packaging", required=True, ondelete="restrict")
    material_id = fields.Many2one("rep.material", related="packaging_id.material_id", store=True)
    weight_kg = fields.Float(string="Weight (kg)")
    tariff_id = fields.Many2one("rep.tariff", string="Tariff Applied")
    amount = fields.Float(string="Eco-contribution (€)")
    source = fields.Selection(
        [("sale", "Quotation Estimate"), ("delivery", "Delivery")], default="delivery")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")], default="confirmed")
    origin = fields.Char(string="Origin Document")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("rep.ledger") or "/"
        return super().create(vals_list)


class RepDeclaration(models.Model):
    _name = "rep.declaration"
    _description = "REP Annual Declaration"
    _inherit = ["mail.thread"]

    name = fields.Char(compute="_compute_name", store=True)
    year = fields.Integer(required=True, default=2026)
    eco_org = fields.Selection(ECO_ORGS, required=True, default="citeo")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("closed", "Closed")], default="draft", tracking=True)
    line_ids = fields.One2many("rep.decl.line", "declaration_id")
    total_tonnage = fields.Float(compute="_compute_totals", store=True)
    total_amount = fields.Float(compute="_compute_totals", store=True)

    @api.depends("year", "eco_org")
    def _compute_name(self):
        for rec in self:
            rec.name = "REP %s - %s" % (rec.year, dict(ECO_ORGS).get(rec.eco_org, ""))

    @api.depends("line_ids.amount", "line_ids.tonnage")
    def _compute_totals(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped("amount"))
            rec.total_tonnage = sum(rec.line_ids.mapped("tonnage"))

    def action_compute(self):
        for rec in self:
            rec.line_ids.unlink()
            # The annual declaration must only aggregate the ledger of its
            # own year. Without this date filter two declarations for
            # different years would produce identical lines.
            groups = self.env["rep.ledger"]._read_group(
                [("company_id", "=", rec.company_id.id),
                 ("state", "=", "confirmed"),
                 ("date", ">=", "%04d-01-01" % rec.year),
                 ("date", "<=", "%04d-12-31" % rec.year)],
                ["material_id", "tariff_id"],
                ["weight_kg:sum", "amount:sum"],
            )
            lines = []
            for material, tariff, weight, amount in groups:
                if not material:
                    continue
                lines.append((0, 0, {
                    "material_id": material.id,
                    "tonnage": (weight or 0.0) / 1000.0,
                    "amount": amount or 0.0,
                }))
            rec.line_ids = lines
            rec.message_post(body="Declaration computed: %s lines." % len(lines))

    def action_export_csv(self):
        import base64
        import csv
        import io
        self.ensure_one()
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(["material", "tonnage_t", "amount_eur"])
        for line in self.line_ids:
            writer.writerow([line.material_id.name, "%.3f" % line.tonnage,
                             "%.2f" % line.amount])
        attachment = self.env["ir.attachment"].create({
            "name": "rep_%s_%s.csv" % (self.year, self.eco_org),
            "raw": base64.b64encode(buffer.getvalue().encode("utf-8")),
            "res_model": self._name, "res_id": self.id, "mimetype": "text/csv",
        })
        return {"type": "ir.actions.act_url",
                "url": "/web/content/%s?download=true" % attachment.id,
                "target": "self"}

    def action_close(self):
        self.write({"state": "closed"})


class RepDeclLine(models.Model):
    _name = "rep.decl.line"
    _description = "REP Declaration Line"

    declaration_id = fields.Many2one("rep.declaration", required=True, ondelete="cascade")
    material_id = fields.Many2one("rep.material", required=True)
    tonnage = fields.Float(string="Tonnage (t)")
    amount = fields.Float(string="Amount (€)")
