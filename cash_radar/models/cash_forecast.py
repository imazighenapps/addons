# -*- coding: utf-8 -*-
import calendar
from datetime import date, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


def add_months(value, months):
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


class CashForecast(models.Model):
    _name = "cash.forecast"
    _description = "Cash Forecast"

    name = fields.Char(
        required=True,
        default=lambda self: "Forecast %s" % fields.Date.context_today(self))
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    date_from = fields.Date(
        required=True, default=fields.Date.context_today)
    weeks = fields.Integer(default=13, required=True)
    delay_days = fields.Integer(
        string="Payment Delay (days)", default=0,
        help="Shift the customer invoices by this number of days to model "
             "a late-paying customer.")
    opening_balance = fields.Monetary(
        string="Opening Balance", currency_field="currency_id")
    horizon_end = fields.Date(compute="_compute_horizon", store=True)
    line_ids = fields.One2many(
        "cash.forecast.line", "forecast_id", string="Lines")
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed")], default="draft")
    total_in = fields.Monetary(
        string="Total Inflow", currency_field="currency_id",
        compute="_compute_totals", store=True)
    total_out = fields.Monetary(
        string="Total Outflow", currency_field="currency_id",
        compute="_compute_totals", store=True)
    net_flow = fields.Monetary(
        string="Net Flow", currency_field="currency_id",
        compute="_compute_totals", store=True)
    min_balance = fields.Monetary(
        string="Lowest Balance", currency_field="currency_id",
        compute="_compute_totals", store=True)
    min_week = fields.Char(string="Lowest Week", compute="_compute_totals",
                           store=True)
    is_at_risk = fields.Boolean(
        string="Cash at Risk", compute="_compute_totals", store=True)

    @api.depends("date_from", "weeks")
    def _compute_horizon(self):
        for forecast in self:
            start = forecast.date_from or fields.Date.context_today(forecast)
            weeks = forecast.weeks or 13
            forecast.horizon_end = start + timedelta(days=7 * weeks)

    @api.depends("line_ids.amount", "line_ids.direction",
                 "line_ids.week_start", "opening_balance")
    def _compute_totals(self):
        for forecast in self:
            total_in = sum(forecast.line_ids.filtered(
                lambda l: l.direction == "in").mapped("amount"))
            total_out = sum(forecast.line_ids.filtered(
                lambda l: l.direction == "out").mapped("amount"))
            forecast.total_in = total_in
            forecast.total_out = total_out
            forecast.net_flow = total_in - total_out
            balance = forecast.opening_balance or 0.0
            lowest = balance
            lowest_week = False
            weeks = sorted(set(forecast.line_ids.mapped("week_start")))
            for week in weeks:
                week_lines = forecast.line_ids.filtered(
                    lambda l, w=week: l.week_start == w)
                balance += sum(week_lines.filtered(
                    lambda l: l.direction == "in").mapped("amount"))
                balance -= sum(week_lines.filtered(
                    lambda l: l.direction == "out").mapped("amount"))
                if balance < lowest:
                    lowest = balance
                    lowest_week = week
            forecast.min_balance = lowest
            forecast.is_at_risk = lowest < 0
            forecast.min_week = "%s-W%02d" % (
                lowest_week.isocalendar()[0],
                lowest_week.isocalendar()[1]) if lowest_week else False

    @api.constrains("weeks")
    def _check_weeks(self):
        for forecast in self:
            if forecast.weeks < 1 or forecast.weeks > 52:
                raise ValidationError(
                    _("A forecast covers between 1 and 52 weeks."))

    def _week_start(self, value):
        return value - timedelta(days=value.weekday())

    def _add_line(self, week, direction, source, amount, partner=False,
                  move=False, recurrence=False):
        if week < self.date_from:
            week = self.date_from
        self.env["cash.forecast.line"].create({
            "forecast_id": self.id,
            "company_id": self.company_id.id,
            "week_start": self._week_start(week),
            "direction": direction,
            "source": source,
            "amount": abs(amount),
            "partner_id": partner.id if partner else False,
            "move_id": move.id if move else False,
            "recurrence_id": recurrence.id if recurrence else False,
        })

    def _compute_invoices(self):
        # Only what falls due inside the projection window: an invoice due
        # years before the opening date belongs to the collection history,
        # not to the thirteen weeks of cash this scenario projects.
        start = self.date_from or fields.Date.context_today(self)
        horizon = self.horizon_end or (start + timedelta(days=7 * self.weeks))
        Move = self.env["account.move"].search([
            ("company_id", "=", self.company_id.id),
            ("state", "=", "posted"),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("move_type", "in", ["out_invoice", "in_invoice", "in_refund",
                                 "out_refund"]),
            ("amount_residual", "!=", 0.0),
            ("invoice_date_due", "!=", False),
            ("invoice_date_due", ">=", start),
            ("invoice_date_due", "<=", horizon),
        ])
        for move in Move:
            due = move.invoice_date_due
            if not due:
                continue
            if move.move_type in ("out_invoice", "out_refund"):
                due = due + timedelta(days=self.delay_days or 0)
                if due > horizon:
                    continue
                direction = "in"
                source = "invoice"
            else:
                direction = "out"
                source = "bill"
            self._add_line(due, direction, source, move.amount_residual,
                           partner=move.partner_id, move=move)

    def _compute_recurrences(self):
        horizon = self.horizon_end
        Recurrence = self.env["cash.forecast.recurrence"].search([
            ("company_id", "=", self.company_id.id),
            ("active", "=", True),
        ])
        for rec in Recurrence:
            current = rec.date_start
            last = rec.date_end or horizon
            guard = 0
            while current and current < horizon and current <= last \
                    and guard < 500:
                guard += 1
                if current >= self.date_from:
                    direction = "in" if rec.amount >= 0 else "out"
                    self._add_line(current, direction, "recurrence",
                                   rec.amount, partner=rec.partner_id,
                                   recurrence=rec)
                if rec.frequency == "weekly":
                    current = current + timedelta(days=7)
                elif rec.frequency == "quarterly":
                    current = add_months(current, 3)
                else:
                    current = add_months(current, 1)

    def action_compute(self):
        for forecast in self:
            forecast.line_ids.unlink()
            forecast._compute_invoices()
            forecast._compute_recurrences()
            forecast.state = "computed"
        return True

    def action_reset(self):
        for forecast in self:
            forecast.line_ids.unlink()
            forecast.state = "draft"
        return True
