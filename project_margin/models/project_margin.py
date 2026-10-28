# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MarginProject(models.Model):
    _name = "margin.project"
    _description = "Project Margin"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        required=True, copy=False, tracking=True,
        help="Short reference of the project, for example PM-2026-014.")
    partner_id = fields.Many2one("res.partner", string="Customer")
    project_id = fields.Many2one(
        "project.project", string="Project",
        help="Odoo project whose costs and revenues are tracked here.")
    manager_id = fields.Many2one(
        "res.users", string="Manager", tracking=True,
        default=lambda self: self.env.user)
    date_start = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(tracking=True)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    budget_revenue = fields.Monetary(
        string="Budget Revenue", currency_field="currency_id",
        tracking=True)
    budget_cost = fields.Monetary(
        string="Budget Cost", currency_field="currency_id", tracking=True)
    alert_threshold = fields.Float(
        string="Alert Threshold (%)", default=10.0,
        help="Cost overrun percentage over the budget cost that triggers "
             "the overrun alert.")
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "margin.line", "project_id", string="Cost and Revenue", copy=True)
    actual_revenue = fields.Monetary(
        string="Actual Revenue", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    actual_cost = fields.Monetary(
        string="Actual Cost", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    actual_margin = fields.Monetary(
        string="Actual Margin", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    budget_margin = fields.Monetary(
        string="Budget Margin", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    margin_rate = fields.Float(
        string="Margin Rate (%)", compute="_compute_amounts", store=True,
        help="Actual margin as a percentage of the actual revenue.")
    cost_ratio = fields.Float(
        string="Cost Ratio (%)", compute="_compute_amounts", store=True,
        help="Actual cost as a percentage of the budget cost.")
    is_overrun = fields.Boolean(
        string="Over Budget", compute="_compute_amounts", store=True,
        help="Set when the actual cost exceeds the budget cost by more than "
             "the alert threshold.")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "The project code must be unique per company.")

    @api.depends("line_ids.line_type", "line_ids.amount",
                 "budget_revenue", "budget_cost", "alert_threshold")
    def _compute_amounts(self):
        for project in self:
            revenue = sum(project.line_ids.filtered(
                lambda line: line.line_type == "revenue").mapped("amount"))
            cost = sum(project.line_ids.filtered(
                lambda line: line.line_type == "cost").mapped("amount"))
            project.actual_revenue = revenue
            project.actual_cost = cost
            project.actual_margin = revenue - cost
            project.budget_margin = (
                project.budget_revenue - project.budget_cost)
            project.margin_rate = (
                (revenue - cost) / revenue * 100.0 if revenue else 0.0)
            project.cost_ratio = (
                cost / project.budget_cost * 100.0
                if project.budget_cost else 0.0)
            project.is_overrun = bool(
                project.budget_cost > 0
                and cost > project.budget_cost
                * (1.0 + (project.alert_threshold or 0.0) / 100.0))

    @api.model_create_multi
    def create(self, vals_list):
        seen = set()
        for vals in vals_list:
            code = (vals.get("code") or "").strip()
            if not code:
                continue
            vals["code"] = code
            company_id = vals.get("company_id") or self.env.company.id
            if (code, company_id) in seen:
                raise ValidationError(_(
                    "The project code \"%s\" is used twice in the same "
                    "company.", code))
            seen.add((code, company_id))
            duplicate = self.with_context(active_test=False).search([
                ("code", "=", code),
                ("company_id", "=", company_id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "The project code \"%s\" is already used by the project "
                    "\"%s\" of the same company.", code, duplicate.name))
        return super().create(vals_list)

    def write(self, vals):
        if "budget_revenue" in vals or "budget_cost" in vals:
            for project in self:
                if project.state == "closed":
                    raise UserError(_(
                        "The budget of the closed project \"%s\" can no "
                        "longer be changed. Reset it to draft first.",
                        project.name))
        return super().write(vals)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for project in self:
            if project.date_end and project.date_start \
                    and project.date_end < project.date_start:
                raise ValidationError(_(
                    "The end date cannot be before the start date."))

    @api.constrains("budget_revenue", "budget_cost", "alert_threshold")
    def _check_budget(self):
        for project in self:
            if project.budget_revenue < 0 or project.budget_cost < 0:
                raise ValidationError(_(
                    "The budget revenue and the budget cost cannot be "
                    "negative."))
            if project.alert_threshold < 0:
                raise ValidationError(_(
                    "The alert threshold cannot be negative."))

    def action_start(self):
        for project in self:
            if project.state != "draft":
                raise UserError(_("Only a draft project can be started."))
            if project.budget_revenue <= 0 and project.budget_cost <= 0:
                raise UserError(_(
                    "Set a budget revenue or a budget cost before starting "
                    "the project."))
            project.state = "running"
            project.message_post(body=_(
                "Project started with a budget of %(revenue)s revenue and "
                "%(cost)s cost.",
                revenue=project.budget_revenue, cost=project.budget_cost))
        return True

    def action_close(self):
        for project in self:
            if project.state != "running":
                raise UserError(_("Only a running project can be closed."))
            project.state = "closed"
            project.message_post(body=_(
                "Project closed with a margin of %(margin)s on %(revenue)s "
                "of actual revenue.",
                margin=project.actual_margin, revenue=project.actual_revenue))
        return True

    def action_reset(self):
        for project in self:
            if project.state != "closed":
                raise UserError(_(
                    "Only a closed project can be reset to draft."))
            project.state = "draft"
            project.message_post(body=_("Project reset to draft."))
        return True

    def action_recompute(self):
        for project in self:
            project.modified(["line_ids"])
        self.env.flush_all()
        for project in self:
            project.message_post(body=_(
                "Totals recomputed from %(count)s cost and revenue line(s).",
                count=len(project.line_ids)))
        return True


class MarginLine(models.Model):
    _name = "margin.line"
    _description = "Project Cost and Revenue Line"
    _order = "project_id, date, id"

    project_id = fields.Many2one(
        "margin.project", string="Project Margin", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    date = fields.Date(required=True, default=fields.Date.context_today)
    line_type = fields.Selection(
        [("revenue", "Revenue"), ("cost", "Cost")], required=True,
        help="Revenue increases the margin, cost decreases it.")
    category = fields.Selection(
        [("labor", "Labor"), ("material", "Material"),
         ("subcontract", "Subcontract"), ("expense", "Expense"),
         ("other", "Other")],
        default="other")
    description = fields.Char(required=True)
    amount = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        related="project_id.currency_id", store=True, readonly=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    invoice_ref = fields.Char(
        string="Invoice Reference",
        help="Customer invoice or supplier bill this line comes from.")
    company_id = fields.Many2one(
        related="project_id.company_id", store=True, readonly=True)

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            if line.amount < 0:
                raise ValidationError(_(
                    "The amount of the line \"%s\" cannot be negative.",
                    line.description))

    @api.model_create_multi
    def create(self, vals_list):
        project_ids = {vals["project_id"] for vals in vals_list
                       if vals.get("project_id")}
        if project_ids:
            closed = self.env["margin.project"].browse(
                sorted(project_ids)).filtered(
                    lambda project: project.state == "closed")
            if closed:
                raise UserError(_(
                    "The project \"%s\" is closed: no cost or revenue line "
                    "can be added to it.", closed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.project_id.state == "closed":
                raise UserError(_(
                    "The project \"%s\" is closed: its cost and revenue "
                    "lines can no longer be changed.", line.project_id.name))
        if vals.get("project_id"):
            target = self.env["margin.project"].browse(vals["project_id"])
            if target.state == "closed":
                raise UserError(_(
                    "The project \"%s\" is closed: no line can be moved to "
                    "it.", target.name))
        return super().write(vals)
