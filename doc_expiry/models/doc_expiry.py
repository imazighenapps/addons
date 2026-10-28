# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ExpiryCategory(models.Model):
    _name = "expiry.category"
    _description = "Document Category"
    _order = "name, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        required=True, help="Short code of the category, for example INS.")
    default_validity_days = fields.Integer(
        default=365, required=True,
        help="Validity applied when a new document is created, in days.")
    reminder_days = fields.Integer(
        default=30, required=True,
        help="Number of days before expiry at which the document is "
             "considered as expiring soon.")
    document_ids = fields.One2many(
        "expiry.document", "category_id", string="Documents")
    document_count = fields.Integer(compute="_compute_document_count")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "The category code must be unique per company.")

    @api.depends("document_ids")
    def _compute_document_count(self):
        for category in self:
            category.document_count = len(category.document_ids)

    @api.constrains("default_validity_days", "reminder_days")
    def _check_days(self):
        for category in self:
            if category.default_validity_days <= 0:
                raise ValidationError(_(
                    "The default validity of category \"%s\" must be "
                    "strictly positive.", category.name))
            if category.reminder_days < 0:
                raise ValidationError(_(
                    "The reminder lead time of category \"%s\" cannot be "
                    "negative.", category.name))


class ExpiryDocument(models.Model):
    _name = "expiry.document"
    _description = "Expiring Document"
    _inherit = ["mail.thread"]
    _order = "expiry_date, id"

    name = fields.Char(required=True, tracking=True)
    reference = fields.Char(
        required=True, tracking=True,
        help="Unique reference of the document, for example the policy "
             "number.")
    category_id = fields.Many2one(
        "expiry.category", string="Category", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Issuer / Counterparty", tracking=True)
    owner_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    issue_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    expiry_date = fields.Date(
        required=True, tracking=True, index=True)
    reminder_days = fields.Integer(
        related="category_id.reminder_days", store=True, readonly=False,
        help="Days before expiry at which the document becomes expiring.")
    state = fields.Selection(
        [("valid", "Valid"), ("expiring", "Expiring Soon"),
         ("expired", "Expired")],
        compute="_compute_expiry", store=True, index=True)
    days_left = fields.Integer(
        string="Days Left", compute="_compute_expiry", store=True)
    reminder_date = fields.Date(
        compute="_compute_expiry", store=True,
        help="Date at which the reminder window opens.")
    log_ids = fields.One2many(
        "expiry.log", "document_id", string="Renewal History")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    _reference_company_uniq = models.Constraint(
        "UNIQUE(reference, company_id)",
        "The document reference must be unique per company.")

    @api.depends("expiry_date", "reminder_days")
    def _compute_expiry(self):
        today = fields.Date.context_today(self)
        for document in self:
            if not document.expiry_date:
                document.state = "valid"
                document.days_left = 0
                document.reminder_date = False
                continue
            remaining = (document.expiry_date - today).days
            reminder_days = document.reminder_days or 0
            document.days_left = remaining
            document.reminder_date = (
                document.expiry_date - timedelta(days=reminder_days))
            if remaining < 0:
                document.state = "expired"
            elif remaining <= reminder_days:
                document.state = "expiring"
            else:
                document.state = "valid"

    @api.onchange("category_id", "issue_date")
    def _onchange_category(self):
        if (self.category_id and self.issue_date
                and not self.expiry_date):
            self.expiry_date = self.issue_date + timedelta(
                days=self.category_id.default_validity_days or 365)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("expiry_date") and vals.get("category_id"):
                category = self.env["expiry.category"].browse(
                    vals["category_id"])
                if vals.get("issue_date"):
                    issue = fields.Date.to_date(vals["issue_date"])
                else:
                    issue = fields.Date.context_today(self)
                vals.setdefault("issue_date", issue)
                vals["expiry_date"] = issue + timedelta(
                    days=category.default_validity_days or 365)
        documents = super().create(vals_list)
        for document in documents:
            self.env["expiry.log"].create({
                "document_id": document.id,
                "date": fields.Date.context_today(self),
                "action": "created",
                "new_expiry": document.expiry_date,
                "user_id": self.env.user.id,
                "note": _("Document registered."),
            })
        return documents

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        for document in self:
            if (document.issue_date and document.expiry_date
                    and document.expiry_date < document.issue_date):
                raise ValidationError(_(
                    "The expiry date of document \"%s\" cannot be before "
                    "its issue date.", document.name))

    def action_renew(self):
        for document in self:
            if not document.active:
                raise UserError(_(
                    "Restore the document before renewing it."))
            if not document.category_id:
                raise UserError(_(
                    "Set a category before renewing the document."))
            today = fields.Date.context_today(self)
            old_expiry = document.expiry_date
            new_expiry = today + timedelta(
                days=document.category_id.default_validity_days or 365)
            document.write({
                "issue_date": today,
                "expiry_date": new_expiry,
            })
            self.env["expiry.log"].create({
                "document_id": document.id,
                "date": today,
                "action": "renewed",
                "old_expiry": old_expiry,
                "new_expiry": new_expiry,
                "user_id": self.env.user.id,
                "note": _("Renewed from the document form."),
            })
        return True

    def action_archive(self):
        for document in self:
            if not document.active:
                raise UserError(_(
                    "This document is already archived."))
            document.active = False
            self.env["expiry.log"].create({
                "document_id": document.id,
                "date": fields.Date.context_today(self),
                "action": "archived",
                "user_id": self.env.user.id,
                "note": _("Document archived."),
            })
        return True

    def action_activate(self):
        for document in self:
            if document.active:
                raise UserError(_(
                    "This document is already active."))
            document.active = True
        return True

    @api.model
    def _cron_check_expiry(self):
        """Refresh the status and log one reminder per document per day."""
        documents = self.search([("active", "=", True)])
        documents.invalidate_recordset(
            ["state", "days_left", "reminder_date"])
        for document in documents:
            document._compute_expiry()
        documents.flush_recordset(
            ["state", "days_left", "reminder_date"])
        today = fields.Date.context_today(self)
        created = 0
        for document in documents:
            if document.state != "expiring":
                continue
            already = document.log_ids.filtered(
                lambda log: log.action == "reminder" and log.date == today)
            if already:
                continue
            self.env["expiry.log"].create({
                "document_id": document.id,
                "date": today,
                "action": "reminder",
                "old_expiry": document.expiry_date,
                "new_expiry": document.expiry_date,
                "user_id": self.env.user.id,
                "note": _(
                    "Reminder: %s day(s) left before expiry.",
                    document.days_left),
            })
            created += 1
        return created


class ExpiryLog(models.Model):
    _name = "expiry.log"
    _description = "Document Renewal Log"
    _order = "date desc, id desc"

    document_id = fields.Many2one(
        "expiry.document", string="Document", required=True,
        ondelete="cascade", index=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today)
    action = fields.Selection(
        [("created", "Created"), ("renewed", "Renewed"),
         ("reminder", "Reminder"), ("archived", "Archived")],
        required=True, default="created")
    old_expiry = fields.Date(string="Previous Expiry")
    new_expiry = fields.Date(string="New Expiry")
    user_id = fields.Many2one(
        "res.users", string="User",
        default=lambda self: self.env.user)
    note = fields.Text()
    company_id = fields.Many2one(
        related="document_id.company_id", store=True)
