# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CancelDeskLog(models.Model):
    _name = "cancel.desk.log"
    _description = "Order Cancellation"
    _inherit = ["mail.thread"]
    _order = "decided_on desc, id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True,
        help="Reference of the cancellation, generated from the CND/ "
             "sequence.")
    document = fields.Char(
        string="Cancelled Order", required=True, tracking=True,
        help="Reference of the order that was cancelled.")
    partner_id = fields.Many2one("res.partner", string="Customer")
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", tracking=True,
        default=lambda self: self.env.user)
    decided_on = fields.Date(
        string="Decided On", required=True,
        default=fields.Date.context_today, tracking=True,
        help="Date the cancellation was decided.")
    decided_by = fields.Many2one(
        "res.users", string="Decided By", tracking=True,
        default=lambda self: self.env.user)
    amount = fields.Monetary(
        string="Lost Value", tracking=True,
        help="Value of the order lost with the cancellation.")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    reason = fields.Selection(
        [("price", "Price"), ("delivery", "Delivery Delay"),
         ("product", "Product Mismatch"), ("competition", "Competitor"),
         ("other", "Other")],
        default="other", required=True, tracking=True)
    state = fields.Selection(
        [("logged", "Logged"), ("written_off", "Written Off"),
         ("recovered", "Recovered")],
        default="logged", required=True, copy=False, tracking=True,
        index=True)
    recovery_ids = fields.One2many(
        "cancel.desk.recovery", "log_id", string="Recoveries")
    recovery_count = fields.Integer(
        string="Recoveries", compute="_compute_recoveries", store=True,
        help="Number of replacement orders won back on this "
             "cancellation.")
    recovered_total = fields.Monetary(
        string="Recovered Value", currency_field="currency_id",
        compute="_compute_recoveries", store=True,
        help="Value won back through the replacement orders.")
    fully_recovered = fields.Boolean(
        string="Fully Recovered", compute="_compute_fully_recovered",
        store=True, help="True when the recovered value reaches the "
             "lost value of the cancellation.")
    written_off = fields.Boolean(default=False, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "cancel.desk.log") or "/"
        return super().create(vals_list)

    @api.depends("recovery_ids", "recovery_ids.amount")
    def _compute_recoveries(self):
        for log in self:
            log.recovery_count = len(log.recovery_ids)
            log.recovered_total = sum(
                log.recovery_ids.mapped("amount"))

    @api.depends("amount", "recovered_total")
    def _compute_fully_recovered(self):
        for log in self:
            log.fully_recovered = bool(
                log.amount > 0
                and log.recovered_total >= log.amount)

    @api.constrains("decided_on")
    def _check_decided_on(self):
        for log in self:
            if log.decided_on and log.decided_on > fields.Date.context_today(
                    log):
                raise ValidationError(_(
                    "The decision date of the cancellation %s cannot be "
                    "in the future.", log.name))

    @api.constrains("amount")
    def _check_amount(self):
        for log in self:
            if log.amount < 0:
                raise ValidationError(_(
                    "The lost value of a cancellation cannot be negative."))

    def action_write_off(self):
        for log in self:
            if log.state != "logged":
                raise UserError(_(
                    "Only a logged cancellation can be written off."))
            log.write({
                "state": "written_off",
                "written_off": True,
            })
            log.message_post(body=_(
                "Loss of %s written off after %s recovery(ies).",
                log.amount, log.recovery_count))
        return True

    def action_reopen(self):
        for log in self:
            if log.state == "logged":
                raise UserError(_(
                    "This cancellation is already logged and open."))
            if log.recovery_count:
                raise UserError(_(
                    "A cancellation with recovered value cannot be "
                    "reopened: %s was won back on it.", log.recovered_total))
            log.state = "logged"
            log.message_post(body=_("Cancellation reopened as logged."))
        return True


class CancelDeskRecovery(models.Model):
    _name = "cancel.desk.recovery"
    _description = "Order Recovery"
    _inherit = ["mail.thread"]
    _order = "recovered_on desc, id desc"

    log_id = fields.Many2one(
        "cancel.desk.log", string="Cancellation", required=True,
        ondelete="cascade", index=True)
    new_ref = fields.Char(
        string="New Order", required=True, tracking=True,
        help="Reference of the replacement order won back.")
    amount = fields.Monetary(
        string="Recovered Amount", required=True,
        help="Value of the replacement order.")
    recovered_on = fields.Date(
        default=fields.Date.context_today, required=True,
        help="Date the replacement order was signed.")
    currency_id = fields.Many2one(
        related="log_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="log_id.company_id", store=True, readonly=True)
    note = fields.Text()

    @api.constrains("amount", "recovered_on")
    def _check_recovery(self):
        for recovery in self:
            if recovery.amount <= 0:
                raise ValidationError(_(
                    "The recovered amount of the order %s must be above "
                    "zero.", recovery.new_ref))
            if recovery.log_id and recovery.log_id.decided_on \
                    and recovery.recovered_on < recovery.log_id.decided_on:
                raise ValidationError(_(
                    "The recovery of the order %s cannot be dated before "
                    "the decision of the cancellation.",
                    recovery.new_ref))

    @api.model_create_multi
    def create(self, vals_list):
        log_ids = {vals["log_id"] for vals in vals_list
                   if vals.get("log_id")}
        if not log_ids:
            return super().create(vals_list)
        logs = self.env["cancel.desk.log"].browse(sorted(log_ids))
        for log in logs:
            if log.state != "logged":
                raise UserError(_(
                    "The cancellation %s is closed: no recovery can be "
                    "added to it.", log.name))
        records = super().create(vals_list)
        for log in logs:
            log.invalidate_recordset()
            if log.fully_recovered:
                log.state = "recovered"
                log.message_post(body=_(
                    "The lost value of %s is fully recovered: %s won "
                    "across %s recovery(ies).", log.amount,
                    log.recovered_total, log.recovery_count))
            elif records.filtered(
                    lambda recovery: recovery.log_id == log):
                log.message_post(body=_(
                    "Recovery registered on %s: %s recovered out of "
                    "%s lost.", log.name,
                    log.recovered_total, log.amount))
        return records

    def write(self, vals):
        for recovery in self:
            if recovery.log_id.state != "logged":
                raise UserError(_(
                    "The cancellation %s is closed: its recoveries can "
                    "no longer be changed.", recovery.log_id.name))
        return super().write(vals)
