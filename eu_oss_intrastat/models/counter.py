# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OssCounter(models.Model):
    _name = "oss.country.counter"
    _description = "Cumulative Cross-Border Sales per Country"
    _inherit = ["mail.thread"]
    _order = "oss_amount desc"

    name = fields.Char(compute="_compute_name", store=True)
    country_id = fields.Many2one("res.country", required=True,
                                 ondelete="restrict")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    year = fields.Integer(default=lambda self: fields.Date.today().year,
                         required=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id,
        required=True)
    oss_amount = fields.Monetary(string="OSS Eligible (goods)")
    ioss_amount = fields.Monetary(string="IOSS Eligible (distance sales)")
    oss_threshold_id = fields.Many2one(
        "oss.threshold", string="OSS Threshold",
        default=lambda self: self.env.ref("eu_oss_intrastat.threshold_oss",
                                          raise_if_not_found=False))
    ioss_threshold_id = fields.Many2one(
        "oss.threshold", string="IOSS Threshold",
        default=lambda self: self.env.ref("eu_oss_intrastat.threshold_ioss",
                                          raise_if_not_found=False))
    oss_limit = fields.Float(related="oss_threshold_id.limit", readonly=True)
    ioss_limit = fields.Float(related="ioss_threshold_id.limit", readonly=True)
    oss_ratio = fields.Float(compute="_compute_state", store=True)
    ioss_ratio = fields.Float(compute="_compute_state", store=True)
    state = fields.Selection(
        [("clear", "Below Threshold"), ("near", "Near Threshold"),
         ("oss_due", "OSS Required"), ("ioss_due", "IOSS Required")],
        compute="_compute_state", store=True, tracking=True)
    move_count = fields.Integer(compute="_compute_state", store=True)

    @api.depends("country_id", "year")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s %s" % (rec.country_id.name or "?", rec.year or "")

    @api.depends("oss_amount", "ioss_amount", "oss_limit", "ioss_limit",
                 "oss_threshold_id.warn_ratio", "ioss_threshold_id.warn_ratio")
    def _compute_state(self):
        for rec in self:
            warn_oss = rec.oss_threshold_id.warn_ratio or 0.8
            warn_ioss = rec.ioss_threshold_id.warn_ratio or 0.8
            rec.oss_ratio = (rec.oss_amount / rec.oss_limit) if rec.oss_limit else 0.0
            rec.ioss_ratio = (rec.ioss_amount / rec.ioss_limit) if rec.ioss_limit else 0.0
            if rec.oss_limit and rec.oss_amount >= rec.oss_limit:
                rec.state = "oss_due"
            elif rec.ioss_limit and rec.ioss_amount >= rec.ioss_limit:
                rec.state = "ioss_due"
            elif (rec.oss_limit and rec.oss_ratio >= warn_oss) or \
                 (rec.ioss_limit and rec.ioss_ratio >= warn_ioss):
                rec.state = "near"
            else:
                rec.state = "clear"

    @api.model
    def _cron_refresh(self):
        """Recompute cumulative amounts from posted customer invoices."""
        year = fields.Date.today().year
        start = "%s-01-01" % year
        existing = {(c.country_id.id, c.year): c for c in
                    self.search([("year", "=", year)])}
        invoices = self.env["account.move"].search([
            ("state", "=", "posted"),
            ("move_type", "=", "out_invoice"),
            ("invoice_date", ">=", start),
        ])
        totals = {}
        for move in invoices:
            country = move.commercial_partner_id.country_id
            if not country:
                continue
            key = country.id
            goods = totals.setdefault(key, {"goods": 0.0, "moves": 0})
            goods["moves"] += 1
            for line in move.invoice_line_ids:
                if not line.product_id.is_storable:
                    goods["goods"] += line.price_total
        for country_id, data in totals.items():
            key = (country_id, year)
            rec = existing.get(key)
            if not rec:
                rec = self.create({"country_id": country_id, "year": year})
            rec.write({"oss_amount": data["goods"],
                       "ioss_amount": data["goods"],
                       "move_count": data["moves"]})
        self.invalidate_recordset()
        return True