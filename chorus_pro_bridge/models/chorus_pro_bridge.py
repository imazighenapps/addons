# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ChorusProConnection(models.Model):
    _name = "chorus.pro.connection"
    _description = "Chorus Pro Connection"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    environment = fields.Selection(
        [("qualification", "Qualification"), ("production", "Production")],
        default="qualification", required=True, tracking=True)
    login = fields.Char(string="Technical Login")
    password_ref = fields.Char(string="Credential Reference")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    submission_ids = fields.One2many("chorus.pro.submission", "connection_id")

    def action_activate(self):
        for rec in self:
            if not rec.login:
                raise UserError(_("Set the technical login before activating."))
            rec.state = "active"
            rec.message_post(body=_("Chorus Pro connection activated."))
        return True


class ChorusProSubmission(models.Model):
    _name = "chorus.pro.submission"
    _description = "Chorus Pro Submission"
    _inherit = ["mail.thread"]
    _order = "submission_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one(
        "chorus.pro.connection", required=True, ondelete="cascade", tracking=True)
    company_id = fields.Many2one(
        related="connection_id.company_id", store=True, readonly=True)
    move_id = fields.Many2one(
        "account.move", string="Customer Invoice", tracking=True)
    partner_id = fields.Many2one("res.partner", string="Public Customer")
    submission_date = fields.Date(default=fields.Date.context_today)
    engagement_code = fields.Char(help="Commitment/engagement code (EJ).")
    service_code = fields.Char(help="Service/execution code.")
    chorus_number = fields.Char(string="Chorus Number", copy=False)
    amount_total = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id,
        required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("submitted", "Submitted"),
         ("accepted", "Accepted"), ("rejected", "Rejected"), ("paid", "Paid")],
        default="draft", required=True, tracking=True)
    rejection_reason = fields.Text()
    payload = fields.Text()
    status_log_ids = fields.One2many("chorus.pro.status.log", "submission_id")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "chorus.pro.submission") or "CHORUS"
        return super().create(vals_list)

    @api.constrains("amount_total")
    def _check_amount(self):
        for rec in self:
            if rec.amount_total < 0:
                raise ValidationError(_("The amount cannot be negative."))

    def action_prepare(self):
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError(_("Only draft or rejected submissions can be prepared."))
            if not rec.engagement_code:
                raise UserError(_("Set the engagement code before preparing."))
            rec.payload = "invoice=%s|ej=%s|service=%s|amount=%s" % (
                rec.move_id.name or "", rec.engagement_code,
                rec.service_code or "", rec.amount_total)
            rec.state = "ready"
            rec.rejection_reason = False
            rec.message_post(body=_("Submission prepared."))
        return True

    def action_submit(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError(_("Only ready submissions can be submitted."))
            if rec.connection_id.state != "active":
                raise UserError(_("Activate the Chorus Pro connection first."))
            rec.state = "submitted"
            rec.chorus_number = rec.chorus_number or ("CHR-%s" % rec.id)
            self.env["chorus.pro.status.log"].create({
                "submission_id": rec.id, "status": "submitted",
                "message": _("Submission sent to Chorus Pro."),
            })
            rec.message_post(body=_("Submitted to Chorus Pro."))
        return True

    def action_mark_accepted(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only submitted invoices can be accepted."))
            rec.state = "accepted"
            self.env["chorus.pro.status.log"].create({
                "submission_id": rec.id, "status": "accepted",
                "message": _("Invoice accepted."),
            })
        return True

    def action_mark_rejected(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only submitted invoices can be rejected."))
            rec.state = "rejected"
            rec.rejection_reason = rec.rejection_reason or _("Rejected by Chorus Pro.")
            self.env["chorus.pro.status.log"].create({
                "submission_id": rec.id, "status": "rejected",
                "message": rec.rejection_reason,
            })
        return True

    def action_mark_paid(self):
        for rec in self:
            if rec.state != "accepted":
                raise UserError(_("Only accepted invoices can be marked paid."))
            rec.state = "paid"
            self.env["chorus.pro.status.log"].create({
                "submission_id": rec.id, "status": "paid",
                "message": _("Payment reported."),
            })
        return True


class ChorusProStatusLog(models.Model):
    _name = "chorus.pro.status.log"
    _description = "Chorus Pro Status Log"
    _order = "create_date desc, id desc"

    submission_id = fields.Many2one(
        "chorus.pro.submission", required=True, ondelete="cascade", index=True)
    status = fields.Char(required=True)
    message = fields.Text()
    company_id = fields.Many2one(
        related="submission_id.company_id", store=True, readonly=True)
