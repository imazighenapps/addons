# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductQualityRule(models.Model):
    _name = "product.quality.rule"
    _description = "Product Quality Rule"
    _order = "field_key, id"

    name = fields.Char(required=True)
    field_key = fields.Selection(
        [("barcode", "Barcode"), ("weight", "Weight"), ("cost", "Cost"),
         ("sale_price", "Sale Price"), ("category", "Category"),
         ("description", "Sales Description")],
        string="Field", required=True,
        help="Field of the product sheet controlled by this rule.")
    severity = fields.Selection(
        [("warning", "Warning"), ("error", "Error")], default="warning",
        required=True,
        help="A warning is a quality issue, an error blocks the clean-up.")
    points = fields.Integer(
        default=5,
        help="Weight of the rule in the score of a scan. A missing field "
             "removes these points from the total.")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    note = fields.Text(
        help="Why the field matters, and what a correct value looks like.")

    _company_field_uniq = models.Constraint(
        "UNIQUE(company_id, field_key)",
        "A field can only be controlled by one rule per company.")

    @api.constrains("points")
    def _check_points(self):
        for rule in self:
            if rule.points < 0:
                raise ValidationError(_(
                    "The points of the rule \"%s\" cannot be negative.",
                    rule.name))

    def _is_missing(self, product):
        """Return True when the product does not satisfy this rule.

        A category is always set by Odoo, so the category rule does not look
        for an empty value: it flags a product that still sits on the
        default category, which means it was never classified.
        """
        self.ensure_one()
        if self.field_key == "barcode":
            return not product.barcode
        if self.field_key == "weight":
            return not product.weight
        if self.field_key == "cost":
            return not product.standard_price
        if self.field_key == "sale_price":
            return not product.list_price
        if self.field_key == "category":
            default_categ = self.env.ref(
                "product.product_category_all", raise_if_not_found=False)
            return bool(default_categ and product.categ_id == default_categ)
        if self.field_key == "description":
            return not (product.description_sale or "").strip()
        return False


class ProductQualityScan(models.Model):
    _name = "product.quality.scan"
    _description = "Product Quality Scan"
    _order = "date_ref desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Quality scan %s")
        % fields.Date.context_today(self))
    date_ref = fields.Date(
        string="Scan Date", required=True,
        default=fields.Date.context_today)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    rule_ids = fields.Many2many(
        "product.quality.rule", "product_quality_scan_rule_rel",
        "scan_id", "rule_id", string="Rules",
        help="Leave empty to use every active rule of the company.")
    product_ids = fields.Many2many(
        "product.product", "product_quality_scan_product_rel",
        "scan_id", "product_id", string="Products to Scan",
        help="Leave empty to scan every active product of the company.")
    scanned_product_ids = fields.Many2many(
        "product.product", "product_quality_scan_scanned_rel",
        "scan_id", "product_id", string="Scanned Products",
        readonly=True, copy=False,
        help="Products covered by the last run of the scan.")
    line_ids = fields.One2many(
        "product.quality.line", "scan_id", string="Anomalies", copy=False)
    product_count = fields.Integer(
        string="Products", compute="_compute_counts", store=True)
    anomaly_count = fields.Integer(
        string="Anomalies", compute="_compute_counts", store=True)
    score = fields.Float(
        string="Score", compute="_compute_counts", store=True,
        help="Completeness of the scanned products, from 0 to 100, weighted "
             "by the points of each rule.")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")], default="draft",
        required=True, copy=False, index=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.rule_id", "rule_ids",
                 "scanned_product_ids")
    def _compute_counts(self):
        for scan in self:
            total_points = sum(scan.rule_ids.mapped("points"))
            missing_points = sum(scan.line_ids.mapped("rule_id.points"))
            scan.product_count = len(scan.scanned_product_ids)
            scan.anomaly_count = len(scan.line_ids)
            if total_points <= 0:
                # No rule, or only rules worth zero point: nothing can be
                # missing, the sheet is complete by definition.
                scan.score = 100.0
                continue
            raw = 100.0 * (1.0 - missing_points / total_points)
            scan.score = round(min(max(raw, 0.0), 100.0), 2)

    def _product_domain(self):
        """Products in the scope of the scan, company filter included."""
        self.ensure_one()
        domain = [
            ("active", "=", True),
            ("company_id", "in", [False, self.company_id.id]),
        ]
        if self.product_ids:
            domain.append(("id", "in", self.product_ids.ids))
        return domain

    def action_run(self):
        Rule = self.env["product.quality.rule"]
        Line = self.env["product.quality.line"]
        for scan in self:
            scan.line_ids.unlink()
            rules = scan.rule_ids
            if not rules:
                rules = Rule.search([
                    ("company_id", "=", scan.company_id.id),
                    ("active", "=", True),
                ])
                scan.rule_ids = [(6, 0, rules.ids)]
            products = self.env["product.product"].search(
                scan._product_domain())
            vals_list = []
            for product in products:
                for rule in rules:
                    if not rule._is_missing(product):
                        continue
                    vals_list.append({
                        "scan_id": scan.id,
                        "product_id": product.id,
                        "rule_id": rule.id,
                    })
            if vals_list:
                Line.create(vals_list)
            scan.scanned_product_ids = [(6, 0, products.ids)]
            scan.state = "done"
            # The counters and the score are stored computed fields: force
            # the recomputation now so the scan is complete on return.
            scan._compute_counts()
        return True

    def action_reset(self):
        for scan in self:
            scan.line_ids.unlink()
            scan.scanned_product_ids = [(6, 0, [])]
            scan.state = "draft"
            scan._compute_counts()
        return True


class ProductQualityLine(models.Model):
    _name = "product.quality.line"
    _description = "Product Quality Anomaly"
    _order = "scan_id, product_id, field_key, id"

    scan_id = fields.Many2one(
        "product.quality.scan", string="Scan", required=True,
        ondelete="cascade", index=True)
    company_id = fields.Many2one(
        related="scan_id.company_id", store=True, readonly=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True,
        ondelete="cascade", index=True)
    rule_id = fields.Many2one(
        "product.quality.rule", string="Rule", ondelete="set null")
    field_key = fields.Selection(
        related="rule_id.field_key", store=True, readonly=True)
    severity = fields.Selection(
        related="rule_id.severity", store=True, readonly=True)
    message = fields.Char(compute="_compute_message")
    state = fields.Selection(
        [("new", "To Fix"), ("fixed", "Fixed"), ("ignored", "Ignored")],
        default="new", required=True, index=True)

    def _missing_label(self, field_key):
        """Readable reason of the anomaly, translated at call time."""
        labels = {
            "barcode": _("barcode is missing"),
            "weight": _("weight is zero"),
            "cost": _("cost is zero"),
            "sale_price": _("sale price is zero"),
            "category": _("product is still on the default category"),
            "description": _("sales description is empty"),
        }
        return labels.get(field_key) or _("data is missing")

    @api.depends("field_key", "product_id")
    def _compute_message(self):
        for line in self:
            line.message = _(
                "%(product)s: %(issue)s",
                product=line.product_id.display_name or _("Unknown product"),
                issue=line._missing_label(line.field_key))

    def action_mark_fixed(self):
        for line in self:
            line.state = "fixed"
        return True

    def action_ignore(self):
        for line in self:
            line.state = "ignored"
        return True
