from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QmsCertification(models.Model):
    _name = "qms.certification"
    _description = "QMS Certification"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expiry_date, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.certification"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    standard_id = fields.Many2one("qms.standard", required=True, ondelete="restrict", check_company=True)
    certification_body_id = fields.Many2one("res.partner", string="Certification Body")
    certificate_number = fields.Char(required=True)
    scope = fields.Text(required=True)
    issue_date = fields.Date()
    expiry_date = fields.Date()
    status = fields.Selection([
        ("draft", "Draft"), ("active", "Active"), ("expiring", "Expiring"),
        ("expired", "Expired"), ("suspended", "Suspended"), ("renewed", "Renewed"),
    ], default="draft", required=True, tracking=True, index=True)
    audit_ids = fields.Many2many("qms.audit", "qms_certification_audit_rel", "certification_id", "audit_id", string="Related Audits")
    audit_count = fields.Integer(compute="_compute_audit_count")
    notes = fields.Text()
    attachment_ids = fields.Many2many("ir.attachment", "qms_certification_attachment_rel", "certification_id", "attachment_id", string="Certificate Files")
    active = fields.Boolean(default=True)

    _certificate_company_uniq = models.Constraint(
        "UNIQUE(certificate_number, company_id)",
        "Certificate numbers must be unique per company.",
    )
    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Certification codes must be unique per company.",
    )

    @api.depends("audit_ids")
    def _compute_audit_count(self):
        for record in self:
            record.audit_count = len(record.audit_ids)

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        for record in self:
            if record.issue_date and record.expiry_date and record.expiry_date < record.issue_date:
                raise ValidationError(_("The certificate expiry date cannot be earlier than the issue date."))

    def action_activate(self):
        for record in self:
            if not record.issue_date or not record.expiry_date:
                raise ValidationError(_("Set issue and expiry dates before activating a certificate."))
        self.write({"status": "active"})
        return True

    def action_suspend(self):
        self.write({"status": "suspended"})
        return True

    def action_mark_renewed(self):
        self.write({"status": "renewed"})
        return True

    @api.model
    def _cron_update_status(self):
        today = fields.Date.context_today(self)
        threshold = fields.Date.add(today, days=90)
        self.search([("status", "in", ["active", "expiring"]), ("expiry_date", "<", today)]).write({"status": "expired"})
        self.search([("status", "=", "active"), ("expiry_date", ">=", today), ("expiry_date", "<=", threshold)]).write({"status": "expiring"})
        return True
