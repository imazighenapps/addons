# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CashForecastLine(models.Model):
    _name = "cash.forecast.line"
    _description = "Cash Forecast Line"
    _order = "week_start, id"

    name = fields.Char(compute="_compute_name", store=True)
    forecast_id = fields.Many2one(
        "cash.forecast", string="Forecast", required=True,
        ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="forecast_id.currency_id", store=True, readonly=True)
    week_start = fields.Date(required=True)
    week_label = fields.Char(compute="_compute_name", store=True)
    direction = fields.Selection(
        [("in", "Inflow"), ("out", "Outflow")],
        required=True, default="in")
    source = fields.Selection(
        [("invoice", "Customer Invoice"), ("bill", "Vendor Bill"),
         ("recurrence", "Recurrence"), ("manual", "Manual")],
        required=True, default="invoice")
    partner_id = fields.Many2one("res.partner", string="Partner")
    move_id = fields.Many2one("account.move", string="Invoice")
    recurrence_id = fields.Many2one(
        "cash.forecast.recurrence", string="Recurrence")
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", required=True)
    state = fields.Selection(
        [("forecast", "Forecast"), ("confirmed", "Confirmed"),
         ("realized", "Realized")],
        default="forecast", required=True)
    note = fields.Text()

    @api.depends("week_start", "direction", "source")
    def _compute_name(self):
        for line in self:
            if line.week_start:
                line.week_label = "%s-W%02d" % (
                    line.week_start.isocalendar()[0],
                    line.week_start.isocalendar()[1])
            else:
                line.week_label = False
            line.name = "%s / %s" % (
                line.week_label or "", line.source or "") \
                or _("Forecast line")
