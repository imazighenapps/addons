# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DupliRule(models.Model):
    _name = "dupli.rule"
    _description = "Duplicate Detection Rule"
    _order = "sequence, id"

    name = fields.Char(required=True, default="Default rule")
    sequence = fields.Integer(default=10)
    day_tolerance = fields.Integer(
        default=7, help="Maximum number of days between two documents.")
    amount_tolerance = fields.Float(
        default=0.0, help="Maximum difference on the total amount.")
    check_invoices = fields.Boolean(string="Invoices and Bills", default=True)
    check_payments = fields.Boolean(string="Payments", default=True)
    active = fields.Boolean(default=True)
    note = fields.Text()


class DupliAlert(models.Model):
    _name = "dupli.alert"
    _description = "Duplicate Alert"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    rule_id = fields.Many2one("dupli.rule", string="Rule", ondelete="set null")
    model_name = fields.Char(string="Model", required=True)
    res_id = fields.Integer(string="Record ID", required=True)
    record_name = fields.Char(string="Document")
    matched_model = fields.Char(string="Matched Model")
    matched_id = fields.Integer(string="Matched ID")
    matched_name = fields.Char(string="Matched Document")
    partner_id = fields.Many2one("res.partner", string="Partner")
    amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    date = fields.Date()
    score = fields.Float(string="Similarity (%)", default=100.0)
    state = fields.Selection(
        [("open", "To Review"), ("ignored", "Not a Duplicate"),
         ("duplicate", "Duplicate Confirmed")],
        default="open", required=True, tracking=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "dupli.alert") or "/"
        return super().create(vals_list)

    def action_ignore(self):
        self.write({"state": "ignored"})

    def action_confirm(self):
        self.write({"state": "duplicate"})

    def action_reset(self):
        self.write({"state": "open"})


class DupliScanner(models.Model):
    _name = "dupli.scanner"
    _description = "Duplicate Scanner"

    @api.model
    def _default_rule(self):
        rule = self.env["dupli.rule"].search([("active", "=", True)], limit=1)
        if not rule:
            rule = self.env["dupli.rule"].create({"name": "Default rule"})
        return rule

    @api.model
    def _alert_exists(self, model_name, res_id, matched_id):
        return bool(self.env["dupli.alert"].search_count([
            ("model_name", "=", model_name),
            ("res_id", "=", res_id),
            ("matched_id", "=", matched_id),
        ]))

    @api.model
    def _compare(self, records, rule, model_name):
        created = 0
        seen = []
        for record in records:
            partner = record.partner_id
            amount = abs(getattr(record, "amount_total", 0.0)
                         or getattr(record, "amount", 0.0))
            date = getattr(record, "invoice_date", False) \
                or getattr(record, "date", False)
            for other, other_amount, other_date in seen:
                if partner != other.partner_id:
                    continue
                if abs(amount - other_amount) > rule.amount_tolerance:
                    continue
                if date and other_date and abs((date - other_date).days) > rule.day_tolerance:
                    continue
                if self._alert_exists(model_name, record.id, other.id):
                    continue
                self.env["dupli.alert"].create({
                    "rule_id": rule.id,
                    "model_name": model_name,
                    "res_id": record.id,
                    "record_name": record.display_name,
                    "matched_model": model_name,
                    "matched_id": other.id,
                    "matched_name": other.display_name,
                    "partner_id": partner.id if partner else False,
                    "amount": amount,
                    "date": date,
                    "score": 100.0 if amount == other_amount else 90.0,
                })
                created += 1
            seen.append((record, amount, date))
        return created

    @api.model
    def action_scan(self):
        rule = self._default_rule()
        created = 0
        if rule.check_invoices:
            moves = self.env["account.move"].search([
                ("state", "=", "posted"),
                ("move_type", "in", ["out_invoice", "in_invoice",
                                     "out_refund", "in_refund"]),
            ], order="invoice_date, id")
            created += self._compare(moves, rule, "account.move")
        if rule.check_payments:
            payments = self.env["account.payment"].search([
                ("state", "not in", ["draft", "canceled", "rejected"]),
            ], order="date, id")
            created += self._compare(payments, rule, "account.payment")
        return created

    def action_scan_ui(self):
        created = self.action_scan()
        return {
            "type": "ir.actions.act_window",
            "name": _("Duplicate Alerts"),
            "res_model": "dupli.alert",
            "view_mode": "list,form",
            "domain": [("state", "=", "open")],
            "help": _("%s new alerts found.") % created,
        }
