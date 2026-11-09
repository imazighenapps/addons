# -*- coding: utf-8 -*-
import calendar
from datetime import date, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TaxRule(models.Model):
    _name = "tax.rule"
    _description = "Tax Deadline Rule"
    _order = "tax_type, name"

    name = fields.Char(required=True)
    tax_type = fields.Selection(
        [("vat", "VAT"), ("corporate", "Corporate Tax"),
         ("payroll", "Payroll"), ("withholding", "Withholding"),
         ("other", "Other")],
        required=True, default="other",
        help="Kind of tax the rule schedules.")
    frequency = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"),
         ("yearly", "Yearly")],
        required=True, default="monthly",
        help="How many periods the rule generates per year.")
    due_day = fields.Integer(
        default=15,
        help="Number of days between the end of the period and the due "
             "date of the deadline.")
    lead_days = fields.Integer(
        default=7,
        help="How many days before the due date the deadline should be "
             "brought to the attention of the accountant.")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    note = fields.Text()
    deadline_ids = fields.One2many(
        "tax.deadline", "rule_id", string="Deadlines", copy=False)

    _sql_constraints = [
        ('company_type_name_uniq', "UNIQUE(company_id, tax_type, name)", "A tax rule with this name and tax type already exists in this "
        "company."),
    ]

    @api.constrains("due_day", "lead_days")
    def _check_days(self):
        for rule in self:
            if rule.due_day < 0:
                raise ValidationError(_(
                    "The due day of the rule \"%s\" cannot be negative.",
                    rule.name))
            if rule.lead_days < 0:
                raise ValidationError(_(
                    "The lead days of the rule \"%s\" cannot be negative.",
                    rule.name))

    def _periods(self, year):
        """Return the (start, end) dates of every period of the year."""
        self.ensure_one()
        if self.frequency == "monthly":
            for month in range(1, 13):
                last_day = calendar.monthrange(year, month)[1]
                yield date(year, month, 1), date(year, month, last_day)
        elif self.frequency == "quarterly":
            for quarter in range(4):
                first_month = quarter * 3 + 1
                last_month = first_month + 2
                last_day = calendar.monthrange(year, last_month)[1]
                yield (date(year, first_month, 1),
                       date(year, last_month, last_day))
        else:
            yield date(year, 1, 1), date(year, 12, 31)

    def _period_label(self, period_start):
        """A short, locale-independent label used in the deadline name."""
        self.ensure_one()
        if self.frequency == "monthly":
            return period_start.strftime("%Y-%m")
        if self.frequency == "quarterly":
            quarter = (period_start.month - 1) // 3 + 1
            return "%s Q%s" % (period_start.year, quarter)
        return str(period_start.year)

    def _generate_year(self, year):
        """Create the deadlines of the year, skipping periods already done."""
        self.ensure_one()
        year = int(year or fields.Date.context_today(self).year)
        Deadline = self.env["tax.deadline"].with_company(self.company_id)
        created = Deadline
        for period_start, period_end in self._periods(year):
            existing = Deadline.search([
                ("rule_id", "=", self.id),
                ("period_start", "=", period_start),
            ], limit=1)
            if existing:
                continue
            created |= Deadline.create({
                "name": "%s %s" % (
                    self.name, self._period_label(period_start)),
                "rule_id": self.id,
                "period_start": period_start,
                "period_end": period_end,
                "due_date": period_end + timedelta(days=self.due_day or 0),
                "note": self.note,
            })
        return created


class TaxDeadline(models.Model):
    _name = "tax.deadline"
    _description = "Tax Deadline"
    _inherit = ["mail.thread"]
    _order = "due_date, id"

    name = fields.Char(required=True, tracking=True)
    rule_id = fields.Many2one(
        "tax.rule", string="Rule", required=True, ondelete="cascade",
        index=True)
    company_id = fields.Many2one(
        related="rule_id.company_id", store=True, readonly=True)
    tax_type = fields.Selection(
        related="rule_id.tax_type", store=True, readonly=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    due_date = fields.Date(required=True, index=True, tracking=True)
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", default=0.0)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    state = fields.Selection(
        [("upcoming", "Upcoming"), ("done", "Done"), ("late", "Late")],
        default="upcoming", required=True, copy=False, tracking=True,
        index=True)
    done_date = fields.Date(readonly=True, copy=False)
    is_late = fields.Boolean(
        string="Overdue", compute="_compute_is_late", store=True,
        help="Set when the due date is passed and the deadline is still "
             "upcoming.")
    days_left = fields.Integer(
        string="Days Left", compute="_compute_days_left",
        help="Days between today and the due date, negative when overdue.")
    note = fields.Text()

    _sql_constraints = [
        ('rule_period_company_uniq', "UNIQUE(rule_id, period_start, company_id)", "A deadline already exists for this rule and this period in this "
        "company."),
    ]

    @api.depends("due_date", "state")
    def _compute_is_late(self):
        today = fields.Date.context_today(self)
        for deadline in self:
            deadline.is_late = bool(
                deadline.due_date
                and deadline.state == "upcoming"
                and deadline.due_date < today)

    @api.depends("due_date")
    def _compute_days_left(self):
        today = fields.Date.context_today(self)
        for deadline in self:
            deadline.days_left = (
                (deadline.due_date - today).days if deadline.due_date else 0)

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for deadline in self:
            if deadline.period_end < deadline.period_start:
                raise ValidationError(_(
                    "The end of the period cannot be before its start on "
                    "the deadline \"%s\".", deadline.name))

    def action_done(self):
        for deadline in self:
            if deadline.state == "done":
                raise UserError(_(
                    "The deadline \"%s\" is already marked as done.",
                    deadline.name))
            deadline.write({
                "state": "done",
                "done_date": fields.Date.context_today(deadline),
            })
        return True

    def action_reset(self):
        for deadline in self:
            if deadline.state == "upcoming":
                raise UserError(_(
                    "The deadline \"%s\" is already upcoming.",
                    deadline.name))
            deadline.write({"state": "upcoming", "done_date": False})
        return True


class TaxCalendarWizard(models.TransientModel):
    _name = "tax.calendar.wizard"
    _description = "Generate Tax Deadlines"

    name = fields.Char(default="Generate Tax Deadlines", required=True)
    year = fields.Integer(
        required=True,
        default=lambda self: fields.Date.context_today(self).year)
    rule_ids = fields.Many2many(
        "tax.rule", string="Rules",
        help="Rules to run. Every rule generates its own periods for the "
             "selected year.")

    def action_generate(self):
        for wizard in self:
            for rule in wizard.rule_ids:
                rule._generate_year(wizard.year)
        return True
