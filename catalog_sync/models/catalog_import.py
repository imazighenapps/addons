# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CatalogImport(models.Model):
    _name = "catalog.import"
    _description = "Supplier Price List"
    _inherit = ["mail.thread"]
    _order = "date_ref desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: "Price List %s" % fields.Date.context_today(self))
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    supplier_id = fields.Many2one(
        "res.partner", string="Supplier", required=True,
        domain=[("supplier_rank", ">", 0)])
    date_ref = fields.Date(
        required=True, default=fields.Date.context_today)
    raw_text = fields.Text(
        string="Price List",
        help="One line per product: reference;price. A tab or a space before "
             "the price is accepted too. Lines starting with # are ignored.")
    line_ids = fields.One2many(
        "catalog.import.line", "import_id", string="Lines")
    state = fields.Selection(
        [("draft", "Draft"), ("simulated", "Simulated"),
         ("applied", "Applied"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    line_count = fields.Integer(compute="_compute_counts", store=True)
    matched_count = fields.Integer(compute="_compute_counts", store=True)
    unmatched_count = fields.Integer(compute="_compute_counts", store=True)
    total_old_cost = fields.Monetary(
        string="Cost Before", currency_field="currency_id",
        compute="_compute_counts", store=True)
    total_new_cost = fields.Monetary(
        string="Cost After", currency_field="currency_id",
        compute="_compute_counts", store=True)
    cost_delta = fields.Monetary(
        string="Cost Variation", currency_field="currency_id",
        compute="_compute_counts", store=True)
    note = fields.Text()

    @api.depends("line_ids.state", "line_ids.old_cost", "line_ids.new_cost")
    def _compute_counts(self):
        for batch in self:
            lines = batch.line_ids.filtered(
                lambda l: l.state in ("matched", "applied"))
            batch.line_count = len(batch.line_ids)
            batch.matched_count = len(lines)
            batch.unmatched_count = len(batch.line_ids) - len(lines)
            batch.total_old_cost = sum(lines.mapped("old_cost"))
            batch.total_new_cost = sum(lines.mapped("new_cost"))
            batch.cost_delta = batch.total_new_cost - batch.total_old_cost

    def _margin_rule(self, product):
        self.ensure_one()
        rules = self.env["catalog.margin.rule"].search([
            ("company_id", "=", self.company_id.id),
            ("active", "=", True),
        ])
        specific = rules.filtered(
            lambda rule: rule.category_id
            and rule.category_id == product.categ_id)[:1]
        return specific or rules.filtered(lambda rule: not rule.category_id)[:1]

    def _match_product(self, reference):
        self.ensure_one()
        product = self.env["product.product"].search(
            [("default_code", "=", reference)], limit=1)
        if product:
            return product
        info = self.env["product.supplierinfo"].search([
            ("partner_id", "=", self.supplier_id.id),
            ("product_code", "=", reference),
        ], limit=1)
        return info.product_tmpl_id.product_variant_id if info \
            else self.env["product.product"]

    @staticmethod
    def _split(raw):
        for separator in (";", "\t"):
            if separator in raw:
                return [part.strip() for part in raw.split(separator, 1)]
        parts = raw.rsplit(None, 1)
        return parts if len(parts) == 2 else None

    def action_simulate(self):
        for batch in self:
            if batch.state == "applied":
                raise UserError(_(
                    "This price list is already applied: create a new one "
                    "for the next update."))
            batch.line_ids.unlink()
            Line = self.env["catalog.import.line"]
            for raw in (batch.raw_text or "").splitlines():
                raw = raw.strip()
                if not raw or raw.startswith("#"):
                    continue
                parts = self._split(raw)
                if not parts:
                    Line.create({
                        "import_id": batch.id,
                        "reference": raw[:64],
                        "state": "unmatched",
                        "note": "No price found on this line.",
                    })
                    continue
                reference, raw_price = parts
                try:
                    cost = float(raw_price.replace(",", "."))
                except ValueError:
                    cost = False
                product = batch._match_product(reference)
                if not product or cost is False:
                    Line.create({
                        "import_id": batch.id,
                        "reference": reference[:64],
                        "product_id": product.id if product else False,
                        "state": "unmatched",
                        "note": "No product matched or the price is invalid.",
                    })
                    continue
                rule = batch._margin_rule(product)
                new_price = rule._sale_price(cost) if rule \
                    else product.list_price
                if rule and not rule.apply_sale_price:
                    new_price = product.list_price
                Line.create({
                    "import_id": batch.id,
                    "reference": reference[:64],
                    "product_id": product.id,
                    "product_name": product.display_name,
                    "old_cost": product.standard_price,
                    "new_cost": cost,
                    "old_price": product.list_price,
                    "new_price": new_price,
                    "state": "matched",
                })
            batch.state = "simulated"
        return True

    def action_apply(self):
        for batch in self:
            if batch.state != "simulated":
                raise UserError(_(
                    "Simulate the price list before applying it."))
            for line in batch.line_ids.filtered(
                    lambda l: l.state == "matched" and l.product_id):
                template = line.product_id.product_tmpl_id.with_company(
                    batch.company_id)
                template.standard_price = line.new_cost
                if line.new_price:
                    template.list_price = line.new_price
                line.state = "applied"
            batch.state = "applied"
            batch.message_post(body=_("Price list applied: %s products.")
                               % batch.matched_count)
        return True

    def action_reset(self):
        for batch in self:
            if batch.state == "applied":
                raise UserError(_(
                    "An applied price list cannot be reset."))
            batch.line_ids.unlink()
            batch.state = "draft"
        return True

    def action_cancel(self):
        for batch in self:
            batch.state = "cancelled"
        return True
