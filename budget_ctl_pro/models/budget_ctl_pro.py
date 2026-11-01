# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BudgetCtl(models.Model):
    _name = "budget.ctl"
    _description = "Budget Control"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        required=True, copy=False, default="/", tracking=True,
        help="Short reference of the budget. Generated from the BGT/ "
             "sequence when left empty.")
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account", ondelete="set null",
        index=True, tracking=True,
        help="Analytic account covered by this budget. Leave empty for a "
             "budget that covers the whole company.")
    date_start = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "budget.ctl.line", "budget_id", string="Budget Lines", copy=True)
    total_planned = fields.Monetary(
        string="Total Planned", currency_field="currency_id",
        compute="_compute_totals", store=True)
    total_actual = fields.Monetary(
        string="Total Actual", currency_field="currency_id",
        compute="_compute_totals", store=True)
    total_committed = fields.Monetary(
        string="Total Committed", currency_field="currency_id",
        compute="_compute_totals", store=True)
    total_available = fields.Monetary(
        string="Total Available", currency_field="currency_id",
        compute="_compute_totals", store=True,
        help="Planned minus actual minus committed, summed over the lines.")
    is_overspent = fields.Boolean(
        string="Overspent", compute="_compute_totals", store=True,
        help="Set when the available amount of the budget is negative.")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "The budget code must be unique per company.")

    @api.depends("line_ids.planned", "line_ids.actual", "line_ids.committed")
    def _compute_totals(self):
        for budget in self:
            planned = sum(budget.line_ids.mapped("planned"))
            actual = sum(budget.line_ids.mapped("actual"))
            committed = sum(budget.line_ids.mapped("committed"))
            budget.total_planned = planned
            budget.total_actual = actual
            budget.total_committed = committed
            budget.total_available = planned - actual - committed
            budget.is_overspent = planned - actual - committed < 0

    @api.model_create_multi
    def create(self, vals_list):
        seen = set()
        for vals in vals_list:
            code = (vals.get("code") or "").strip()
            if not code or code == "/":
                code = self.env["ir.sequence"].next_by_code("budget.ctl") or "/"
            vals["code"] = code
            company_id = vals.get("company_id") or self.env.company.id
            if (code, company_id) in seen:
                raise ValidationError(_(
                    "The budget code \"%s\" is used twice in the same "
                    "company.", code))
            seen.add((code, company_id))
            duplicate = self.with_context(active_test=False).search([
                ("code", "=", code),
                ("company_id", "=", company_id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "The budget code \"%s\" is already used by the budget "
                    "\"%s\" of the same company.", code, duplicate.name))
        return super().create(vals_list)

    def write(self, vals):
        locked = {"date_start", "date_end", "analytic_account_id"}
        if locked & set(vals):
            for budget in self:
                if budget.state == "closed":
                    raise UserError(_(
                        "The period and the analytic scope of the closed "
                        "budget \"%s\" can no longer be changed. Reset it to "
                        "draft first.", budget.name))
        return super().write(vals)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for budget in self:
            if budget.date_start and budget.date_end \
                    and budget.date_end < budget.date_start:
                raise ValidationError(_(
                    "The end date of the budget \"%s\" cannot be before its "
                    "start date.", budget.name))

    def action_start(self):
        for budget in self:
            if budget.state != "draft":
                raise UserError(_("Only a draft budget can be started."))
            if not budget.line_ids:
                raise UserError(_(
                    "Add at least one budget line before starting the budget "
                    "\"%s\".", budget.name))
            budget.state = "running"
            budget.message_post(body=_(
                "Budget started with %(planned).2f planned, %(actual).2f "
                "actual and %(committed).2f committed.",
                planned=budget.total_planned, actual=budget.total_actual,
                committed=budget.total_committed))
        return True

    def action_close(self):
        for budget in self:
            if budget.state != "running":
                raise UserError(_("Only a running budget can be closed."))
            budget.state = "closed"
            budget.message_post(body=_(
                "Budget closed with %(available).2f still available on "
                "%(planned).2f planned.",
                available=budget.total_available,
                planned=budget.total_planned))
        return True

    def action_reset(self):
        for budget in self:
            if budget.state != "closed":
                raise UserError(_(
                    "Only a closed budget can be reset to draft."))
            budget.state = "draft"
            budget.message_post(body=_("Budget reset to draft."))
        return True


class BudgetCtlLine(models.Model):
    _name = "budget.ctl.line"
    _description = "Budget Control Line"
    _order = "budget_id, sequence, id"

    budget_id = fields.Many2one(
        "budget.ctl", string="Budget", required=True, ondelete="cascade",
        index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Description", required=True)
    planned = fields.Monetary(
        string="Planned", currency_field="currency_id",
        help="Amount granted to this line for the budget period.")
    actual = fields.Monetary(
        string="Actual", currency_field="currency_id",
        help="Amount already invoiced or booked on this line. A negative "
             "value records a credit or a reversal.")
    committed = fields.Monetary(
        string="Committed", currency_field="currency_id",
        help="Amount already engaged by a purchase order or a signed "
             "commitment but not invoiced yet.")
    available = fields.Monetary(
        string="Available", currency_field="currency_id",
        compute="_compute_available", store=True,
        help="Planned minus actual minus committed.")
    note = fields.Text()
    currency_id = fields.Many2one(
        related="budget_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="budget_id.company_id", store=True, readonly=True)

    @api.depends("planned", "actual", "committed")
    def _compute_available(self):
        for line in self:
            line.available = line.planned - line.actual - line.committed

    @api.constrains("planned", "committed")
    def _check_amounts(self):
        for line in self:
            if line.planned < 0:
                raise ValidationError(_(
                    "The planned amount of the line \"%s\" cannot be "
                    "negative.", line.name))
            if line.committed < 0:
                raise ValidationError(_(
                    "The committed amount of the line \"%s\" cannot be "
                    "negative.", line.name))

    @api.model_create_multi
    def create(self, vals_list):
        budget_ids = {vals["budget_id"] for vals in vals_list
                      if vals.get("budget_id")}
        if budget_ids:
            closed = self.env["budget.ctl"].browse(
                sorted(budget_ids)).filtered(
                    lambda budget: budget.state == "closed")
            if closed:
                raise UserError(_(
                    "The budget \"%s\" is closed: no budget line can be "
                    "added to it.", closed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.budget_id.state == "closed":
                raise UserError(_(
                    "The budget \"%s\" is closed: its lines can no longer be "
                    "changed.", line.budget_id.name))
        if vals.get("budget_id"):
            target = self.env["budget.ctl"].browse(vals["budget_id"])
            if target.state == "closed":
                raise UserError(_(
                    "The budget \"%s\" is closed: no line can be moved to "
                    "it.", target.name))
        return super().write(vals)

    def unlink(self):
        for line in self:
            if line.budget_id.state == "closed":
                raise UserError(_(
                    "The budget \"%s\" is closed: its lines can no longer be "
                    "deleted.", line.budget_id.name))
        return super().unlink()
