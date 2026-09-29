import hashlib

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QmsEvidence(models.Model):
    _name = "qms.evidence"
    _description = "QMS Evidence"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "evidence_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(default=lambda self: self.env["ir.sequence"].next_by_code("qms.evidence"), required=True, copy=False, index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    evidence_type = fields.Selection(
        [("document", "Document"), ("photo", "Photo"), ("record", "Record"), ("training", "Training"), ("inspection", "Inspection"), ("measurement", "Measurement"), ("certificate", "Certificate"), ("meeting", "Meeting Record"), ("system", "System Record"), ("other", "Other")],
        default="record",
        required=True,
    )
    evidence_date = fields.Date(default=fields.Date.context_today, required=True)
    valid_from = fields.Date()
    valid_until = fields.Date()
    status = fields.Selection([("draft", "Draft"), ("valid", "Valid"), ("expired", "Expired"), ("rejected", "Rejected")], default="draft", tracking=True, required=True)
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user, check_company=True)
    source = fields.Char()
    description = fields.Text()
    attachment_ids = fields.Many2many("ir.attachment", "qms_evidence_attachment_rel", "evidence_id", "attachment_id", string="Attachments")
    integrity_hash = fields.Char(readonly=True, copy=False, index=True)
    requirement_ids = fields.Many2many("qms.requirement", "qms_requirement_evidence_rel", "evidence_id", "requirement_id", string="Requirements")
    control_ids = fields.Many2many("qms.control", "qms_evidence_control_rel", "evidence_id", "control_id", string="Controls")

    @api.constrains("valid_from", "valid_until")
    def _check_validity_dates(self):
        for record in self:
            if record.valid_from and record.valid_until and record.valid_until < record.valid_from:
                raise ValidationError(_("The evidence expiry date cannot be earlier than its start date."))

    def action_validate(self):
        for record in self:
            record._refresh_integrity_hash()
            record.status = "valid"
        return True

    def action_reject(self):
        self.write({"status": "rejected"})
        return True

    def action_expire(self):
        self.write({"status": "expired"})
        return True

    @api.model
    def _cron_expire_records(self):
        today = fields.Date.context_today(self)
        self.search([("status", "=", "valid"), ("valid_until", "<", today)]).write({"status": "expired"})
        return True

    def _refresh_integrity_hash(self):
        for record in self:
            hasher = hashlib.sha256()
            attachments = record.attachment_ids.sorted(key=lambda attachment: attachment.id or 0)
            for attachment in attachments:
                payload = attachment.raw or b""
                hasher.update(str(attachment.id).encode())
                hasher.update(payload)
            if not attachments:
                hasher.update((record.name or "").encode())
                hasher.update((record.description or "").encode())
            record.integrity_hash = hasher.hexdigest()
