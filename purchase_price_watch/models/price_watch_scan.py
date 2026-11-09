# -*- coding: utf-8 -*-
from datetime import datetime, time

from odoo import fields, models, _


class PriceScanWizard(models.TransientModel):
    _name = "price.scan.wizard"
    _description = "Supplier Price Scan"
    _order = "id"

    name = fields.Char(default="Price scan")
    date_from = fields.Date()
    date_to = fields.Date()
    rule_ids = fields.Many2many("price.watch.rule", string="Rules")

    def action_scan(self):
        rules = self.rule_ids
        if not rules:
            rules = self.env["price.watch.rule"].search([
                ("company_id", "=", self.env.company.id),
                ("active", "=", True)])
        for rule in rules:
            rule._scan_prices(
                self.env["purchase.order"], self.date_from, self.date_to)
        return True


class PriceWatchRule(models.Model):
    _inherit = "price.watch.rule"

    def _scan_prices(self, PurchaseOrder, date_from, date_to):
        """Compare every confirmed line of the window with the last price.

        The comparison is anchored on each rule, so a rule never reads the
        orders of another company and the test can prove the isolation.
        """
        self.ensure_one()
        orders = PurchaseOrder.search([
            ("state", "in", ("purchase", "done")),
            ("company_id", "=", self.company_id.id),
        ])
        lines = [
            line for order in orders for line in order.order_line
            if self._in_window(line, date_from, date_to)
        ]
        previous_prices = {}
        alerts_to_create = []
        for line in sorted(
                lines,
                key=lambda item: (item.order_id.date_order or "", item.id)):
            key = (line.product_id.id, line.order_id.partner_id.id)
            previous = previous_prices.get(key)
            previous_prices[key] = line.price_unit or 0.0
            if not previous:
                continue
            variation = (line.price_unit or 0.0) - previous
            if not previous or abs(variation / previous * 100.0) \
                    < self.threshold_pct:
                continue
            if self.env["price.watch"].search_count([
                    ("order_line_id", "=", line.id)]):
                continue
            alerts_to_create.append({
                "product_id": line.product_id.id,
                "partner_id": line.order_id.partner_id.id,
                "previous_price": previous,
                "new_price": line.price_unit or 0.0,
                "order_id": line.order_id.id,
                "order_line_id": line.id,
                "company_id": self.company_id.id,
            })
        for values in alerts_to_create:
            alert = self.env["price.watch"].with_company(
                self.company_id).create(values)
            alert.message_post(
                body=_("The unit price moved from %s to %s compared with "
                       "the last order for this vendor.")
                % (values["previous_price"], values["new_price"]))

    def _in_window(self, line, date_from, date_to):
        """True when the order date falls inside the scan window (if any).

        date_order is a Datetime while the wizard fields are Dates, so the
        comparison is normalized before it is evaluated.
        """
        day = line.order_id.date_order
        if not day:
            return True
        if date_from and day < datetime.combine(
                date_from, datetime.min.time()):
            return False
        if date_to and day > datetime.combine(
                date_to, datetime.max.time()):
            return False
        return True
