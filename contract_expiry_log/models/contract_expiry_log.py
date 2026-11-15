# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContractExpiryLog(models.Model):
    _name = "contract.expiry.log"
    _description = "Contract Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "end_date, id"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, index=True,
        tracking=True)
    contract_type = fields.Selection(
        [("customer", "Customer"), ("supplier", "Supplier"),
         ("lease", "Lease"), ("service", "Service"), ("other", "Other")],
        string="Type", default="other", tracking=True)
    start_date = fields.Date(tracking=True)
    end_date = fields.Date(string="Expiry Date", required=True, index=True,
                           tracking=True)
    notice_date = fields.Date(
        string="Notice Date", tracking=True,
        help="Date by which a renewal or termination decision is needed.")
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    days_to_expiry = fields.Integer(
        compute="_compute_days_to_expiry", store=True, index=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"),
         ("expiring", "Expiring Soon"), ("renewed", "Renewed"),
         ("closed", "Closed")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.depends("end_date")
    def _compute_days_to_expiry(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.end_date:
                record.days_to_expiry = (record.end_date - today).days
            else:
                record.days_to_expiry = 0

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date \
                    and record.end_date < record.start_date:
                raise ValidationError(
                    _("The expiry date cannot be before the start date."))

    def action_activate(self):
        for record in self:
            if record.state not in ("draft", "expiring"):
                raise UserError(_("Only a draft or expiring contract can be activated."))
            record.state = "active"
        return True

    def action_mark_expiring(self):
        for record in self:
            if record.state != "active":
                raise UserError(_("Only an active contract can be marked expiring."))
            record.state = "expiring"
        return True

    def action_renew(self):
        for record in self:
            if record.state not in ("active", "expiring"):
                raise UserError(_("Only an active or expiring contract can be renewed."))
            record.state = "renewed"
        return True

    def action_close(self):
        for record in self:
            if record.state == "closed":
                raise UserError(_("This contract is already closed."))
            record.state = "closed"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("closed", "renewed"):
                raise UserError(_("Only a closed or renewed contract can be reset to draft."))
            record.state = "draft"
        return True
