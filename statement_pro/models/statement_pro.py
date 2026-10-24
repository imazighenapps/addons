# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StatementRun(models.Model):
    _name = "statement.run"
    _description = "Partner Statement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_to desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    date_from = fields.Date(
        required=True, default=lambda self: fields.Date.context_today(self).replace(day=1))
    date_to = fields.Date(
        required=True, default=fields.Date.context_today)
    line_ids = fields.One2many("statement.line", "statement_id", string="Movements")
    opening_balance = fields.Monetary(
        currency_field="currency_id", readonly=True)
    total_debit = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    total_credit = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    closing_balance = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    overdue_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent")],
        default="draft", required=True, tracking=True)
    sent_date = fields.Date(readonly=True)
    note = fields.Text()
    line_count = fields.Integer(compute="_compute_totals", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "statement.run") or "/"
        return super().create(vals_list)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for statement in self:
            if statement.date_from > statement.date_to:
                raise UserError(_("The start date must be before the end date."))

    @api.depends("line_ids.debit", "line_ids.credit", "line_ids.date_maturity",
                 "opening_balance")
    def _compute_totals(self):
        today = fields.Date.context_today(self)
        for statement in self:
            lines = statement.line_ids
            statement.total_debit = sum(lines.mapped("debit"))
            statement.total_credit = sum(lines.mapped("credit"))
            statement.closing_balance = (
                statement.opening_balance
                + statement.total_debit - statement.total_credit)
            statement.overdue_amount = sum(
                lines.filtered(
                    lambda l: l.date_maturity and l.date_maturity < today
                ).mapped("balance"))
            statement.line_count = len(lines)

    def _receivable_domain(self):
        self.ensure_one()
        accounts = self.env["account.account"].search([
            ("account_type", "in", ["asset_receivable", "liability_payable"]),
            ("company_ids", "in", self.company_id.id),
        ])
        return [
            ("partner_id", "=", self.partner_id.id),
            ("parent_state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
            ("account_id", "in", accounts.ids),
        ]

    def action_generate(self):
        for statement in self:
            statement.line_ids.unlink()
            domain = statement._receivable_domain()
            opening_lines = self.env["account.move.line"].search(
                domain + [("date", "<", statement.date_from)])
            opening = sum(opening_lines.mapped("balance"))
            moves = self.env["account.move.line"].search(
                domain + [("date", ">=", statement.date_from),
                          ("date", "<=", statement.date_to)],
                order="date, id")
            balance = opening
            vals_list = []
            for line in moves:
                balance += line.balance
                vals_list.append({
                    "statement_id": statement.id,
                    "date": line.date,
                    "move_id": line.move_id.id,
                    "reference": line.move_id.name,
                    "label": line.name or line.move_id.name,
                    "debit": line.debit,
                    "credit": line.credit,
                    "balance": balance,
                    "date_maturity": line.date_maturity,
                })
            statement.write({
                "opening_balance": opening,
                "line_ids": [(0, 0, vals) for vals in vals_list],
                "state": "draft",
            })
            if not vals_list and not opening:
                raise UserError(_(
                    "No posted journal item was found for %s on this period.",
                    statement.partner_id.display_name))
        return True

    def action_send(self):
        for statement in self:
            if not statement.line_ids:
                raise UserError(_("Generate the statement before sending it."))
            statement.write({
                "state": "sent",
                "sent_date": fields.Date.context_today(statement),
            })
            statement.message_post(body=_(
                "Statement %(name)s sent to %(partner)s.",
                name=statement.name,
                partner=statement.partner_id.display_name))
        return True

    def action_reset(self):
        self.write({"state": "draft", "sent_date": False})

    def action_print(self):
        return self.env.ref(
            "statement_pro.action_report_statement").report_action(self)


class StatementLine(models.Model):
    _name = "statement.line"
    _description = "Statement Line"
    _order = "date, id"

    statement_id = fields.Many2one(
        "statement.run", required=True, ondelete="cascade", index=True)
    date = fields.Date(required=True)
    move_id = fields.Many2one("account.move", string="Journal Entry")
    reference = fields.Char()
    label = fields.Char()
    debit = fields.Monetary(currency_field="currency_id")
    credit = fields.Monetary(currency_field="currency_id")
    balance = fields.Monetary(currency_field="currency_id")
    date_maturity = fields.Date(string="Due Date")
    currency_id = fields.Many2one(
        related="statement_id.currency_id", store=True, readonly=True)


class StatementBatch(models.TransientModel):
    _name = "statement.batch"
    _description = "Generate Statements in Batch"

    date_from = fields.Date(
        required=True, default=lambda self: fields.Date.context_today(self).replace(day=1))
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    partner_ids = fields.Many2many(
        "res.partner", string="Partners",
        help="Leave empty to use every customer with a posted movement.")
    only_customers = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    def action_generate(self):
        self.ensure_one()
        partners = self.partner_ids
        if not partners:
            domain = [("parent_state", "=", "posted"),
                      ("company_id", "=", self.company_id.id),
                      ("partner_id", "!=", False)]
            if self.only_customers:
                domain.append(("account_id.account_type", "=", "asset_receivable"))
            else:
                domain.append(("account_id.account_type", "=", "liability_payable"))
            lines = self.env["account.move.line"].search(domain)
            partners = lines.mapped("partner_id")
        created = self.env["statement.run"]
        for partner in partners:
            statement = self.env["statement.run"].create({
                "partner_id": partner.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "company_id": self.company_id.id,
            })
            statement.action_generate()
            created |= statement
        return {
            "type": "ir.actions.act_window",
            "name": _("Statements"),
            "res_model": "statement.run",
            "view_mode": "list,form",
            "domain": [("id", "in", created.ids)],
        }
