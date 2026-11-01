# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class JobCost(models.Model):
    _name = "job.cost"
    _description = "Job Cost Sheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        required=True, copy=False, tracking=True,
        help="Short reference of the job, for example JOB/2026/0042.")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", tracking=True,
        help="Customer who ordered the job and pays its revenue.")
    project_id = fields.Many2one(
        "project.project", string="Project", tracking=True,
        help="Odoo project whose tasks and timesheets belong to this job.")
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
        string="Alert Threshold (%)", default=10.0, tracking=True,
        help="Accepted overrun, in percent of the budget cost, before the "
             "job is flagged as over budget.")
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "job.cost.line", "job_id", string="Cost Lines", copy=True)
    actual_revenue = fields.Monetary(
        string="Actual Revenue", currency_field="currency_id", tracking=True,
        help="Revenue invoiced or accrued on the job so far. The margin is "
             "computed from this amount.")
    actual_cost = fields.Monetary(
        string="Actual Cost", currency_field="currency_id",
        compute="_compute_amounts", store=True,
        help="Invoiced cost: the sum of the cost lines that are not "
             "committed.")
    committed_cost = fields.Monetary(
        string="Committed Cost", currency_field="currency_id",
        compute="_compute_amounts", store=True,
        help="Cost already engaged but not invoiced yet: the sum of the "
             "committed cost lines.")
    margin = fields.Monetary(
        string="Margin", currency_field="currency_id",
        compute="_compute_amounts", store=True,
        help="Actual revenue minus actual cost minus committed cost.")
    margin_rate = fields.Float(
        string="Margin Rate (%)", compute="_compute_amounts", store=True,
        help="Margin as a percentage of the actual revenue.")
    progress_pct = fields.Float(
        string="Progress (%)", compute="_compute_amounts", store=True,
        readonly=False,
        help="Actual plus committed cost as a percentage of the budget cost, "
             "bounded between 0 and 100. Computed automatically, and editable "
             "when the physical progress of the job differs from its cost "
             "consumption.")
    is_overrun = fields.Boolean(
        string="Over Budget", compute="_compute_amounts", store=True,
        help="Set when actual plus committed cost exceeds the budget cost by "
             "more than the alert threshold.")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_company_uniq', "UNIQUE(code, company_id)", "The job code must be unique per company."),
    ]

    @api.depends("line_ids.amount", "line_ids.is_committed",
                 "actual_revenue", "budget_cost", "alert_threshold")
    def _compute_amounts(self):
        for job in self:
            actual = sum(job.line_ids.filtered(
                lambda line: not line.is_committed).mapped("amount"))
            committed = sum(job.line_ids.filtered(
                lambda line: line.is_committed).mapped("amount"))
            consumed = actual + committed
            job.actual_cost = actual
            job.committed_cost = committed
            job.margin = (job.actual_revenue or 0.0) - consumed
            job.margin_rate = (
                job.margin / job.actual_revenue * 100.0
                if job.actual_revenue else 0.0)
            job.progress_pct = min(
                100.0, max(0.0, consumed / job.budget_cost * 100.0)
            ) if job.budget_cost else 0.0
            job.is_overrun = bool(
                job.budget_cost > 0 and consumed > job.budget_cost
                * (1.0 + (job.alert_threshold or 0.0) / 100.0))

    @api.model_create_multi
    def create(self, vals_list):
        seen = set()
        for vals in vals_list:
            code = (vals.get("code") or "").strip()
            if not code:
                code = self.env["ir.sequence"].next_by_code(
                    "job.cost") or "/"
            vals["code"] = code
            company_id = vals.get("company_id") or self.env.company.id
            if (code, company_id) in seen:
                raise ValidationError(_(
                    "The job code \"%s\" is used twice in the same company.",
                    code))
            seen.add((code, company_id))
            duplicate = self.with_context(active_test=False).search([
                ("code", "=", code),
                ("company_id", "=", company_id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "The job code \"%s\" is already used by the job \"%s\" "
                    "of the same company.", code, duplicate.name))
        return super().create(vals_list)

    def write(self, vals):
        locked = {"budget_revenue", "budget_cost", "alert_threshold"}
        if locked & set(vals):
            for job in self:
                if job.state == "closed":
                    raise UserError(_(
                        "The budget of the closed job \"%s\" can no longer be "
                        "changed. Reset the job to draft first.", job.name))
        return super().write(vals)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for job in self:
            if job.date_end and job.date_start \
                    and job.date_end < job.date_start:
                raise ValidationError(_(
                    "The end date of the job \"%s\" cannot be before its "
                    "start date.", job.name))

    @api.constrains("budget_revenue", "budget_cost", "alert_threshold")
    def _check_budget(self):
        for job in self:
            if job.budget_revenue < 0 or job.budget_cost < 0:
                raise ValidationError(_(
                    "The budget revenue and the budget cost of the job "
                    "\"%s\" cannot be negative.", job.name))
            if job.alert_threshold < 0:
                raise ValidationError(_(
                    "The alert threshold of the job \"%s\" cannot be "
                    "negative.", job.name))

    @api.constrains("progress_pct")
    def _check_progress(self):
        for job in self:
            if not 0.0 <= job.progress_pct <= 100.0:
                raise ValidationError(_(
                    "The progress of the job \"%s\" must stay between 0 and "
                    "100 percent.", job.name))

    def action_start(self):
        for job in self:
            if job.state != "draft":
                raise UserError(_(
                    "Only a draft job can be started, and \"%s\" is not "
                    "draft.", job.name))
            if job.budget_revenue <= 0 and job.budget_cost <= 0:
                raise UserError(_(
                    "Set a budget revenue or a budget cost on the job \"%s\" "
                    "before starting it.", job.name))
            job.state = "running"
            job.message_post(body=_(
                "Job started with a budget of %(revenue)s revenue and "
                "%(cost)s cost.",
                revenue=job.budget_revenue, cost=job.budget_cost))
        return True

    def action_close(self):
        for job in self:
            if job.state != "running":
                raise UserError(_(
                    "Only a running job can be closed, and \"%s\" is not "
                    "running.", job.name))
            job.state = "closed"
            job.message_post(body=_(
                "Job closed with %(actual)s actual cost, %(committed)s "
                "committed cost and a margin of %(margin)s.",
                actual=job.actual_cost, committed=job.committed_cost,
                margin=job.margin))
        return True

    def action_reset(self):
        for job in self:
            if job.state != "closed":
                raise UserError(_(
                    "Only a closed job can be reset to draft, and \"%s\" is "
                    "not closed.", job.name))
            job.state = "draft"
            job.message_post(body=_(
                "Job reopened: the budget and the cost lines are editable "
                "again."))
        return True

    def action_recompute(self):
        for job in self:
            job.modified(["line_ids"])
        self.env.flush_all()
        for job in self:
            job.message_post(body=_(
                "Totals recomputed from %(count)s cost line(s): "
                "%(actual)s actual, %(committed)s committed.",
                count=len(job.line_ids), actual=job.actual_cost,
                committed=job.committed_cost))
        return True


class JobCostLine(models.Model):
    _name = "job.cost.line"
    _description = "Job Cost Line"
    _order = "job_id, date, id"

    job_id = fields.Many2one(
        "job.cost", string="Job Cost", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    date = fields.Date(required=True, default=fields.Date.context_today)
    cost_type = fields.Selection(
        [("labor", "Labor"), ("material", "Material"),
         ("subcontract", "Subcontract"), ("overhead", "Overhead"),
         ("other", "Other")],
        string="Cost Type", required=True, default="other", tracking=True,
        help="Nature of the cost: labor, material, subcontract, overhead or "
             "other.")
    description = fields.Char(required=True)
    amount = fields.Monetary(required=True, currency_field="currency_id")
    is_committed = fields.Boolean(
        string="Committed", tracking=True,
        help="Set for a cost already engaged - purchase order sent, "
             "subcontract signed - but not invoiced yet. A committed line "
             "feeds the committed cost and the margin, not the actual cost.")
    invoice_ref = fields.Char(
        string="Invoice Reference",
        help="Supplier bill or purchase order this cost comes from.")
    partner_id = fields.Many2one("res.partner", string="Vendor")
    currency_id = fields.Many2one(
        related="job_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="job_id.company_id", store=True, readonly=True)

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            if line.amount < 0:
                raise ValidationError(_(
                    "The amount of the cost line \"%s\" cannot be negative.",
                    line.description))

    @api.model_create_multi
    def create(self, vals_list):
        job_ids = {vals["job_id"] for vals in vals_list
                   if vals.get("job_id")}
        if job_ids:
            closed = self.env["job.cost"].browse(
                sorted(job_ids)).filtered(
                    lambda job: job.state == "closed")
            if closed:
                raise UserError(_(
                    "The job \"%s\" is closed: no cost line can be added to "
                    "it.", closed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.job_id.state == "closed":
                raise UserError(_(
                    "The job \"%s\" is closed: its cost lines can no longer "
                    "be changed.", line.job_id.name))
        if vals.get("job_id"):
            target = self.env["job.cost"].browse(vals["job_id"])
            if target.state == "closed":
                raise UserError(_(
                    "The job \"%s\" is closed: no cost line can be moved to "
                    "it.", target.name))
        return super().write(vals)

    def unlink(self):
        for line in self:
            if line.job_id.state == "closed":
                raise UserError(_(
                    "The job \"%s\" is closed: its cost lines can no longer "
                    "be deleted.", line.job_id.name))
        return super().unlink()
