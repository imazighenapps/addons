# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PriceWatch(models.Model):
    _name = "price.watch"
    _description = "Price Movement Alert"
    _inherit = ["mail.thread"]
    _order = "date_ref desc, id desc"

    product_id = fields.Many2one(
        "product.product", string="Product", required=True)
    partner_id = fields.Many2one(
        "res.partner", string="Vendor", required=True)
    previous_price = fields.Monetary(
        string="Previous price", currency_field="currency_id")
    new_price = fields.Monetary(
        string="New price", currency_field="currency_id")
    variation_pct = fields.Float(compute="_compute_variation", store=True)
    date_ref = fields.Date(default=fields.Date.context_today)
    order_id = fields.Many2one(
        "purchase.order", string="Purchase Order", ondelete="cascade",
        index=True)
    order_line_id = fields.Many2one(
        "purchase.order.line", string="Order Line", ondelete="cascade")
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    state = fields.Selection(
        [("new", "New"), ("reviewed", "Reviewed"),
         ("ignored", "Ignored")],
        default="new", required=True, index=True)
    note = fields.Text()

    _sql_constraints = [
        ('line_uniq', "unique(order_line_id)", "An alert already exists for this order line."),
    ]

    @api.depends("previous_price", "new_price")
    def _compute_variation(self):
        for alert in self:
            previous = alert.previous_price or 0.0
            if previous:
                alert.variation_pct = (
                    (alert.new_price - previous) / previous * 100.0)
            else:
                alert.variation_pct = 0.0

    def action_review(self):
        for alert in self.filtered(lambda item: item.state == "new"):
            alert.write({"state": "reviewed"})
        return True

    def action_ignore(self):
        for alert in self.filtered(lambda item: item.state != "ignored"):
            alert.write({"state": "ignored"})
        return True

    def action_reopen(self):
        for alert in self:
            alert.write({"state": "new"})
        return True
