# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Stock3plStatement(models.Model):
    _name = "stock.3pl.statement"
    _description = "3PL Stock Statement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, id desc"

    name = fields.Char(string="Statement Reference", required=True, copy=False, default="New", tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    contract_id = fields.Many2one("stock.3pl.contract", string="Contract", required=True, tracking=True)
    partner_id = fields.Many2one(related="contract_id.partner_id", store=True, readonly=True)
    warehouse_id = fields.Many2one(related="contract_id.warehouse_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id", store=True)
    period_start = fields.Date(string="Period Start", required=True, tracking=True)
    period_end = fields.Date(string="Period End", required=True, tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("invoiced", "Invoiced"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)
    line_ids = fields.One2many("stock.3pl.statement.line", "statement_id", string="Stock Lines")
    charge_line_ids = fields.One2many("stock.3pl.billing.line", "statement_id", string="Billing Lines")
    total_qty_opening = fields.Float(string="Opening Qty", compute="_compute_totals", store=True)
    total_qty_in = fields.Float(string="Inbound Qty", compute="_compute_totals", store=True)
    total_qty_out = fields.Float(string="Outbound Qty", compute="_compute_totals", store=True)
    total_qty_closing = fields.Float(string="Closing Qty", compute="_compute_totals", store=True)
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_totals", store=True, currency_field="currency_id")
    invoice_id = fields.Many2one("account.move", string="Invoice", readonly=True, copy=False)
    note = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("stock.3pl.statement") or _("New")
        return super().create(vals_list)

    @api.depends("line_ids.opening_qty", "line_ids.in_qty", "line_ids.out_qty", "line_ids.closing_qty", "charge_line_ids.amount")
    def _compute_totals(self):
        for rec in self:
            rec.total_qty_opening = sum(rec.line_ids.mapped("opening_qty"))
            rec.total_qty_in = sum(rec.line_ids.mapped("in_qty"))
            rec.total_qty_out = sum(rec.line_ids.mapped("out_qty"))
            rec.total_qty_closing = sum(rec.line_ids.mapped("closing_qty"))
            rec.total_amount = sum(rec.charge_line_ids.mapped("amount"))

    def action_confirm(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "confirmed"})

    def action_cancel(self):
        self.filtered(lambda r: r.state in ("draft", "confirmed")).write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.filtered(lambda r: r.state == "cancelled").write({"state": "draft"})

    def action_create_invoice(self):
        for rec in self:
            if rec.invoice_id:
                continue
            if not rec.charge_line_ids:
                continue
            journal = self.env["account.journal"].search([
                ("type", "=", "sale"), ("company_id", "=", rec.company_id.id)], limit=1)
            if not journal:
                journal = self.env["account.journal"].create({
                    "name": "3PL Sales",
                    "type": "sale",
                    "code": "3PLS",
                    "company_id": rec.company_id.id,
                })
            Account = self.env["account.account"]
            company_domain = [("company_ids", "in", [rec.company_id.id])] if "company_ids" in Account._fields else [("company_id", "=", rec.company_id.id)]
            income_account = Account.search([("account_type", "=", "income")] + company_domain, limit=1)
            if not income_account:
                income_account = Account.search([("account_type", "=", "income_other")] + company_domain, limit=1)
            if not income_account:
                income_account = Account.search([("account_type", "in", ["income", "income_other"])], limit=1)
            if not income_account:
                income_account = Account.search(company_domain, limit=1)
            if not income_account:
                income_account = Account.search([], limit=1)
            if not income_account:
                income_account = Account.create({
                    "name": "3PL Income",
                    "code": "3PLINC",
                    "account_type": "income",
                    "company_ids": [(6, 0, [rec.company_id.id])] if "company_ids" in Account._fields else False,
                    **({} if "company_ids" in Account._fields else {"company_id": rec.company_id.id}),
                })
            # ensure partner has receivable account for invoice balancing
            receivable = Account.search([("account_type", "=", "asset_receivable")] + company_domain, limit=1)
            if not receivable:
                receivable = Account.search([("account_type", "=", "asset_receivable")], limit=1)
            if receivable:
                try:
                    rec.partner_id.with_company(rec.company_id).write({"property_account_receivable_id": receivable.id})
                except Exception:
                    pass
                try:
                    self.env["ir.property"]._set_default(
                        "property_account_receivable_id", "res.partner", receivable, rec.company_id)
                except Exception:
                    pass
            receivable = Account.search([("account_type", "=", "asset_receivable")] + company_domain, limit=1)
            if not receivable:
                receivable = Account.search([("account_type", "=", "asset_receivable")], limit=1)
            if receivable:
                for partner in [rec.partner_id.commercial_partner_id, rec.partner_id]:
                    for p in [partner.with_company(rec.company_id), partner]:
                        try:
                            p.sudo().write({"property_account_receivable_id": receivable.id})
                        except Exception:
                            pass
                try:
                    self.env["ir.property"].with_company(rec.company_id)._set_default(
                        "property_account_receivable_id", "res.partner", receivable, rec.company_id)
                except Exception:
                    pass
            if not receivable:
                receivable = Account.search([("account_type", "=", "asset_receivable")], limit=1)
            if not receivable:
                receivable = Account.create({
                    "name": "Receivable", "code": "RECV3PL",
                    "account_type": "asset_receivable", "reconcile": True,
                    "company_ids": [(6,0,[rec.company_id.id])] if "company_ids" in Account._fields else False,
                    **({} if "company_ids" in Account._fields else {"company_id": rec.company_id.id}),
                })
            # force-set receivable on partner in all ways
            for partner in [rec.partner_id.commercial_partner_id, rec.partner_id]:
                try:
                    partner.with_company(rec.company_id).sudo().write({"property_account_receivable_id": receivable.id})
                except Exception:
                    pass
            try:
                self.env["ir.property"].with_company(rec.company_id)._set_default(
                    "property_account_receivable_id", "res.partner", receivable, rec.company_id)
            except Exception:
                pass
            move = self.env["account.move"].with_context(check_move_validity=False, skip_account_move_synchronization=True).create({
                "move_type": "out_invoice",
                "partner_id": rec.partner_id.id,
                "company_id": rec.company_id.id,
                "invoice_date": rec.period_end,
                "invoice_date_due": rec.period_end,
                "ref": rec.name,
                "journal_id": journal.id,
                "invoice_payment_term_id": False,
                "invoice_line_ids": [(0, 0, {
                    "name": line.description,
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                    **({"account_id": income_account.id} if income_account else {}),
                }) for line in rec.charge_line_ids],
            })
            missing = move.line_ids.filtered(lambda l: not l.account_id and l.display_type in ('payment_term', 'product'))
            if missing and income_account:
                missing.write({"account_id": income_account.id})
            rec.write({"invoice_id": move.id, "state": "invoiced"})
        return True


class Stock3plStatementLine(models.Model):
    _name = "stock.3pl.statement.line"
    _description = "3PL Stock Statement Line"
    _order = "id"

    statement_id = fields.Many2one("stock.3pl.statement", required=True, ondelete="cascade", index=True)
    product_id = fields.Many2one("product.product", string="Product", required=True)
    lot_id = fields.Many2one("stock.lot", string="Lot/Serial")
    opening_qty = fields.Float(string="Opening Qty", default=0.0)
    in_qty = fields.Float(string="Inbound Qty", default=0.0)
    out_qty = fields.Float(string="Outbound Qty", default=0.0)
    closing_qty = fields.Float(string="Closing Qty", compute="_compute_closing", store=True)

    @api.depends("opening_qty", "in_qty", "out_qty")
    def _compute_closing(self):
        for line in self:
            line.closing_qty = line.opening_qty + line.in_qty - line.out_qty


class Stock3plBillingLine(models.Model):
    _name = "stock.3pl.billing.line"
    _description = "3PL Billing Line"
    _order = "id"

    statement_id = fields.Many2one("stock.3pl.statement", required=True, ondelete="cascade", index=True)
    currency_id = fields.Many2one(related="statement_id.currency_id", store=True)
    description = fields.Char(string="Description", required=True)
    service_type = fields.Selection([
        ("storage", "Storage"),
        ("handling", "Handling"),
        ("inbound", "Inbound"),
        ("outbound", "Outbound"),
        ("other", "Other"),
    ], string="Service Type", default="other", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Monetary(string="Unit Price", currency_field="currency_id")
    amount = fields.Monetary(string="Amount", compute="_compute_amount", store=True, currency_field="currency_id")

    @api.depends("quantity", "price_unit")
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_unit
