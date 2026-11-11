# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CertDocument(models.Model):
    _name = "cert.document"
    _description = "Supplier Certificate"
    _inherit = ["mail.thread"]
    _order = "expiry_date, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, tracking=True,
        index=True)
    cert_type = fields.Selection(
        [("iso", "ISO"), ("organic", "Organic"), ("halal", "Halal"),
         ("kosher", "Kosher"), ("other", "Other")],
        string="Certificate Type", required=True, default="iso",
        tracking=True)
    reference = fields.Char(
        string="Certificate Reference",
        help="Reference number printed on the certificate.")
    issue_date = fields.Date(
        string="Issue Date", required=True, default=fields.Date.context_today,
        tracking=True)
    expiry_date = fields.Date(
        string="Expiry Date", required=True, tracking=True)
    reminder_date = fields.Date(
        compute="_compute_reminder_date", store=True,
        help="Date to review the certificate before it expires.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("valid", "Valid"),
         ("expiring", "Expiring Soon"), ("expired", "Expired"),
         ("renewed", "Renewed")],
        default="draft", required=True, tracking=True, index=True, copy=False)
    renewal_count = fields.Integer(
        compute="_compute_renewal_count", store=True)
    renewal_ids = fields.One2many(
        "cert.renewal", "certificate_id", string="Renewals")
    blocked = fields.Boolean(
        compute="_compute_blocked", store=True,
        help="True when the certificate is expired and should block use.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()
    active = fields.Boolean(default=True)

    @api.depends("expiry_date")
    def _compute_reminder_date(self):
        for cert in self:
            cert.reminder_date = (
                cert.expiry_date - relativedelta(days=30)
                if cert.expiry_date else False)

    @api.depends("renewal_ids")
    def _compute_renewal_count(self):
        for cert in self:
            cert.renewal_count = len(cert.renewal_ids)

    @api.depends("state")
    def _compute_blocked(self):
        for cert in self:
            cert.blocked = cert.state == "expired"

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        for cert in self:
            if cert.expiry_date < cert.issue_date:
                raise ValidationError(_(
                    "The expiry date of %s cannot come before its issue date.",
                    cert.name))

    def _check_not_expired(self):
        for cert in self:
            if cert.expiry_date and cert.expiry_date < fields.Date.context_today(cert):
                raise UserError(_(
                    "Certificate %s is expired. Renew it before marking it valid.",
                    cert.name))

    def action_mark_valid(self):
        for cert in self:
            if cert.state not in ("draft", "renewed"):
                raise UserError(_("Only draft or renewed certificates can be validated."))
            cert._check_not_expired()
            cert.state = "valid"
            cert.message_post(body=_("The certificate is now valid."))
        return True

    def action_mark_expiring(self):
        for cert in self:
            if cert.state != "valid":
                raise UserError(_("Only valid certificates can be marked as expiring."))
            cert.state = "expiring"
            cert.message_post(body=_("The certificate is expiring soon."))
        return True

    def action_mark_expired(self):
        for cert in self:
            if cert.state not in ("valid", "expiring"):
                raise UserError(_("Only valid or expiring certificates can expire."))
            cert.state = "expired"
            cert.message_post(body=_("The certificate has expired."))
        return True

    def action_renew(self):
        for cert in self:
            if cert.state != "expired":
                raise UserError(_("Only expired certificates can be renewed."))
            old_expiry = cert.expiry_date or fields.Date.context_today(cert)
            new_issue = old_expiry
            new_expiry = old_expiry + relativedelta(years=1)
            self.env["cert.renewal"].create({
                "certificate_id": cert.id,
                "previous_expiry_date": cert.expiry_date,
                "new_issue_date": new_issue,
                "new_expiry_date": new_expiry,
            })
            cert.write({
                "issue_date": new_issue,
                "expiry_date": new_expiry,
                "state": "renewed",
            })
            cert.message_post(body=_(
                "The certificate was renewed until %s.", new_expiry))
        return True
