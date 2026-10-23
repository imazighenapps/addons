# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class IntrastatLine(models.Model):
    _name = "intrastat.line"
    _description = "Intrastat Declaration Line"
    _order = "period desc, id"

    name = fields.Char(default="/", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    direction = fields.Selection(
        [("dispatch", "Dispatch (EU → other MS)"),
         ("arrival", "Arrival (other MS → EU)")],
        required=True, default="dispatch")
    period = fields.Char(required=True,
                         default=lambda self: fields.Date.today().strftime("%Y-%m"))
    move_id = fields.Many2one("account.move", required=True,
                              ondelete="cascade")
    partner_country_id = fields.Many2one("res.country",
                                         string="Partner Country",
                                         ondelete="restrict")
    product_code = fields.Char(string="CN / Commodity Code")
    country_code = fields.Char(compute="_compute_codes", store=True)
    partner_code = fields.Char(compute="_compute_codes", store=True)
    amount = fields.Monetary(compute="_compute_amount", store=True)
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id")
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready to Declare"),
         ("declared", "Declared")],
        default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "intrastat.line") or "/"
        return super().create(vals_list)

    @api.depends("partner_country_id")
    def _compute_codes(self):
        for rec in self:
            code = rec.partner_country_id.code or ""
            rec.country_code = code
            rec.partner_code = ("%s%s" % (code, rec.move_id.partner_id.id))[:12]

    @api.depends("move_id", "move_id.amount_untaxed")
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.move_id.amount_untaxed

    def action_mark_ready(self):
        self.write({"state": "ready"})

    def action_mark_declared(self):
        for rec in self:
            if not rec.country_code:
                raise UserError(
                    "Set the partner country before declaring this line.")
        self.write({"state": "declared"})

    def cron_prepare_lines(self):
        """Public wrapper so the cron (and operators) can prepare lines.

        Odoo 20 blocks remote calls to methods starting with an underscore,
        so ``_cron_prepare`` stays private and this delegates to it.
        """
        return self._cron_prepare()

    @api.model
    def _cron_prepare(self):
        """Create draft lines from posted invoices that lack one."""
        moves = self.env["account.move"].search([
            ("state", "=", "posted"),
            ("move_type", "=", "out_invoice"),
        ], order="invoice_date desc", limit=200)
        created = 0
        for move in moves:
            if self.search_count([("move_id", "=", move.id)]):
                continue
            if not move.commercial_partner_id.country_id:
                continue
            self.create({
                "move_id": move.id,
                "partner_country_id": move.commercial_partner_id.country_id.id,
                "period": (move.invoice_date or fields.Date.today()).strftime("%Y-%m"),
            })
            created += 1
        return created