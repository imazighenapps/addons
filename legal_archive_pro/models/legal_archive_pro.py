# -*- coding: utf-8 -*-
import base64
import binascii
import hashlib
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

GENESIS_HASH = "0" * 64


class ArchiveDocument(models.Model):
    _name = "archive.document"
    _description = "Archived Legal Document"
    _inherit = ["mail.thread"]
    _order = "document_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    document_type = fields.Selection(
        [("invoice", "Customer Invoice"), ("bill", "Supplier Bill"),
         ("contract", "Contract"), ("payslip", "Payslip"),
         ("other", "Other")],
        required=True, default="other", tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Counterparty", tracking=True)
    reference = fields.Char(
        required=True, copy=False, tracking=True,
        help="Unique reference of the document, for example the invoice "
             "number.")
    document_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    retention_years = fields.Integer(
        string="Retention (Years)", default=10, required=True,
        tracking=True, help="Legal retention period in years.")
    expiry_date = fields.Date(
        compute="_compute_expiry_date", store=True, index=True,
        help="Date at which the retention period ends and the file may be "
             "purged.")
    state = fields.Selection(
        [("active", "Active"), ("archived", "Archived"),
         ("purged", "Purged")],
        default="active", required=True, copy=False, tracking=True,
        index=True)
    hash = fields.Char(
        string="Hash", copy=False, readonly=True,
        help="SHA-256 of the previous hash followed by the file bytes.")
    previous_hash = fields.Char(
        string="Previous Hash", copy=False, readonly=True,
        help="Hash of the last document sealed before this one in the same "
             "company.")
    file_data = fields.Binary(string="Document File")
    file_name = fields.Char(string="File Name")
    log_ids = fields.One2many(
        "archive.log", "document_id", string="Audit Log")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('reference_company_uniq', "UNIQUE(reference, company_id)", "The document reference must be unique per company."),
    ]

    @api.depends("document_date", "retention_years")
    def _compute_expiry_date(self):
        for document in self:
            if document.document_date and document.retention_years > 0:
                document.expiry_date = document.document_date + timedelta(
                    days=365 * document.retention_years)
            else:
                document.expiry_date = False

    @api.model_create_multi
    def create(self, vals_list):
        seen = set()
        for vals in vals_list:
            reference = (vals.get("reference") or "").strip()
            if not reference:
                continue
            vals["reference"] = reference
            company_id = vals.get("company_id") or self.env.company.id
            if (reference, company_id) in seen:
                raise ValidationError(_(
                    "The document reference \"%s\" is used twice in the "
                    "same company.", reference))
            seen.add((reference, company_id))
            duplicate = self.with_context(active_test=False).search([
                ("reference", "=", reference),
                ("company_id", "=", company_id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "The document reference \"%s\" is already used by the "
                    "document \"%s\" of the same company.",
                    reference, duplicate.name))
        documents = super().create(vals_list)
        for document in documents:
            document._log("created", _("Document registered in the archive."))
        return documents

    @api.constrains("document_date")
    def _check_document_date(self):
        for document in self:
            if (document.document_date
                    and document.document_date
                    > fields.Date.context_today(self)):
                raise ValidationError(_(
                    "The document date of \"%s\" cannot be in the future.",
                    document.name))

    @api.constrains("retention_years")
    def _check_retention(self):
        for document in self:
            if document.retention_years < 1:
                raise ValidationError(_(
                    "The retention period of \"%s\" must be at least one "
                    "year.", document.name))

    def _decode_file(self):
        """Return the raw bytes of the stored file."""
        self.ensure_one()
        data = self.file_data or b""
        if isinstance(data, str):
            data = data.encode("ascii")
        try:
            return base64.b64decode(data, validate=True)
        except (binascii.Error, ValueError):
            return data

    def _previous_company_hash(self):
        """Hash of the last document sealed in the same company."""
        last = self.search([
            ("company_id", "=", self.company_id.id),
            ("hash", "!=", False),
        ], order="id desc", limit=1)
        return last.hash or GENESIS_HASH

    def _log(self, action, note):
        self.ensure_one()
        return self.env["archive.log"].create({
            "document_id": self.id,
            "date": fields.Date.context_today(self),
            "action": action,
            "user_id": self.env.user.id,
            "note": note,
        })

    def action_seal(self):
        for document in self:
            if document.state != "active":
                raise UserError(_("Only an active document can be sealed."))
            if not document.file_data:
                raise UserError(_(
                    "Attach a file to \"%s\" before sealing it.",
                    document.name))
            previous_hash = document._previous_company_hash()
            digest = hashlib.sha256(
                previous_hash.encode("utf-8")
                + document._decode_file()).hexdigest()
            document.previous_hash = previous_hash
            document.hash = digest
            document.flush_recordset(["hash", "previous_hash"])
            document._log("sealed", _(
                "Document sealed: SHA-256 %(hash)s computed after hash "
                "%(previous)s.", hash=digest, previous=previous_hash))
        return True

    def action_verify(self):
        for document in self:
            if not document.hash:
                raise UserError(_(
                    "Seal the document \"%s\" before verifying it.",
                    document.name))
            if not document.file_data:
                raise UserError(_(
                    "The file of \"%s\" has been purged: nothing is left "
                    "to verify.", document.name))
            digest = hashlib.sha256(
                (document.previous_hash or GENESIS_HASH).encode("utf-8")
                + document._decode_file()).hexdigest()
            if digest == document.hash:
                document._log("verified", _(
                    "Verification succeeded: the file matches the sealed "
                    "hash."))
            else:
                document._log("verified", _(
                    "Verification failed: the file does not match the "
                    "sealed hash."))
                raise UserError(_(
                    "The hash of \"%s\" does not match: the file was "
                    "modified after its last sealing.", document.name))
        return True

    def action_archive(self):
        for document in self:
            if document.state != "active":
                raise UserError(_("Only an active document can be archived."))
            document.state = "archived"
            document._log("archived", _(
                "Document archived: removed from the active register."))
        return True

    def action_purge(self):
        today = fields.Date.context_today(self)
        for document in self:
            if document.state != "archived":
                raise UserError(_("Only an archived document can be purged."))
            if document.expiry_date > today:
                raise UserError(_(
                    "The retention period of \"%s\" runs until %s: the "
                    "file cannot be purged before that date.",
                    document.name, document.expiry_date))
            document.file_data = False
            document.state = "purged"
            document._log("purged", _(
                "File purged after the retention period; the hash and the "
                "audit log are kept."))
        return True


class ArchiveLog(models.Model):
    _name = "archive.log"
    _description = "Archive Audit Log"
    _order = "date desc, id desc"

    document_id = fields.Many2one(
        "archive.document", string="Document", required=True,
        ondelete="cascade", index=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today)
    action = fields.Selection(
        [("created", "Created"), ("viewed", "Viewed"),
         ("exported", "Exported"), ("verified", "Verified"),
         ("sealed", "Sealed"), ("archived", "Archived"),
         ("purged", "Purged")],
        required=True, default="created")
    user_id = fields.Many2one(
        "res.users", string="User",
        default=lambda self: self.env.user)
    note = fields.Text()
    company_id = fields.Many2one(
        related="document_id.company_id", store=True)
