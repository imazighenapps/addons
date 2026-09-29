from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QmsDocument(models.Model):
    _name = "qms.document"
    _description = "QMS Controlled Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code, id"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.document"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user, check_company=True)
    document_type = fields.Selection([
        ("policy", "Policy"), ("procedure", "Procedure"), ("instruction", "Work Instruction"),
        ("form", "Form / Template"), ("manual", "Manual"), ("record", "Record"), ("other", "Other"),
    ], default="procedure", required=True)
    state = fields.Selection([
        ("draft", "Draft"), ("review", "Under Review"), ("approval", "Pending Approval"),
        ("published", "Published"), ("obsolete", "Obsolete"),
    ], default="draft", tracking=True, required=True, index=True)
    description = fields.Html()
    current_version_id = fields.Many2one("qms.document.version", string="Current Version", copy=False)
    version_ids = fields.One2many("qms.document.version", "document_id", string="Versions")
    requirement_ids = fields.Many2many("qms.requirement", "qms_document_requirement_rel", "document_id", "requirement_id", string="Requirements")
    process_ids = fields.Many2many("qms.process", "qms_document_process_rel", "document_id", "process_id", string="Processes")
    review_date = fields.Date()
    publication_date = fields.Date(readonly=True)
    ack_ids = fields.One2many("qms.document.ack", "document_id", string="Acknowledgements")
    active = fields.Boolean(default=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Document codes must be unique per company.",
    )

    @api.constrains("owner_id", "company_id")
    def _check_owner_company(self):
        for record in self:
            if record.owner_id and record.owner_id.company_id and record.owner_id.company_id != record.company_id:
                raise ValidationError(_("The document owner must belong to the same company."))

    def _require_version(self):
        for record in self:
            if not record.current_version_id:
                raise UserError(_("Create and select a document version before approving or publishing the document."))

    def action_create_version(self):
        for record in self:
            if record.state == "obsolete":
                raise UserError(_("An obsolete document cannot receive a new revision."))
            version_no = len(record.version_ids) + 1
            version = self.env["qms.document.version"].create({
                "document_id": record.id,
                "revision": str(version_no),
                "prepared_by_id": self.env.user.id,
                "content_note": "New controlled revision",
            })
            record.current_version_id = version
            record.state = "draft"
        return True

    def action_submit_review(self):
        for record in self:
            record._require_version()
            if record.state != "draft":
                raise UserError(_("Only draft documents can be submitted for review."))
        self.write({"state": "review"})
        return True

    def action_request_approval(self):
        for record in self:
            if record.state != "review":
                raise UserError(_("Only documents under review can be sent for approval."))
        self.write({"state": "approval"})
        return True

    def action_approve(self):
        for record in self:
            record._require_version()
            if not record.current_version_id.reviewer_id:
                raise UserError(_("Assign a reviewer on the current version before approval."))
            if record.current_version_id.reviewer_id != self.env.user:
                raise UserError(_("Only the assigned reviewer can approve this document revision."))
            if record.current_version_id.prepared_by_id == self.env.user:
                raise UserError(_("The document preparer cannot approve the same revision."))
            record.current_version_id.write({"state": "approved", "approved_by_id": self.env.user.id, "approval_date": fields.Date.context_today(self)})
            record.state = "approval"
        return True

    def action_publish(self):
        for record in self:
            record._require_version()
            if record.current_version_id.state != "approved":
                raise UserError(_("The current version must be approved before publication."))
            record.write({"state": "published", "publication_date": fields.Date.context_today(self)})
            record.current_version_id.write({"state": "published"})
        return True

    def action_obsolete(self):
        self.write({"state": "obsolete", "active": False})
        return True


class QmsDocumentVersion(models.Model):
    _name = "qms.document.version"
    _description = "QMS Document Revision"
    _order = "document_id, id desc"

    document_id = fields.Many2one("qms.document", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one("res.company", related="document_id.company_id", store=True, index=True, readonly=True)
    revision = fields.Char(required=True)
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", required=True, default=lambda self: self.env.user, check_company=True)
    reviewer_id = fields.Many2one("res.users", string="Reviewer", check_company=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, check_company=True)
    approval_date = fields.Date(readonly=True)
    published_date = fields.Date(readonly=True)
    state = fields.Selection([
        ("draft", "Draft"), ("review", "Under Review"), ("approved", "Approved"), ("published", "Published"), ("obsolete", "Obsolete"),
    ], default="draft", required=True)
    content_note = fields.Text()
    attachment_ids = fields.Many2many("ir.attachment", "qms_document_version_attachment_rel", "version_id", "attachment_id", string="Files")

    _revision_document_uniq = models.Constraint(
        "UNIQUE(document_id, revision)",
        "Revision numbers must be unique within a document.",
    )

    @api.constrains("reviewer_id", "company_id", "prepared_by_id")
    def _check_reviewer_company(self):
        for record in self:
            if record.reviewer_id and record.reviewer_id.company_id and record.reviewer_id.company_id != record.company_id:
                raise ValidationError(_("The reviewer must belong to the document company."))
            if record.reviewer_id and record.prepared_by_id == record.reviewer_id:
                raise ValidationError(_("The document preparer and reviewer must be different users."))


class QmsDocumentAck(models.Model):
    _name = "qms.document.ack"
    _description = "QMS Document Acknowledgement"
    _order = "acknowledged_on desc, id desc"

    document_id = fields.Many2one("qms.document", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one("res.company", related="document_id.company_id", store=True, index=True, readonly=True)
    version_id = fields.Many2one("qms.document.version", required=True, ondelete="restrict")
    employee_user_id = fields.Many2one("res.users", string="Employee", required=True, default=lambda self: self.env.user)
    acknowledged_on = fields.Datetime(readonly=True)
    status = fields.Selection([("pending", "Pending"), ("acknowledged", "Acknowledged")], default="pending", required=True)
    note = fields.Char()

    def action_acknowledge(self):
        self.ensure_one()
        if self.employee_user_id != self.env.user and not self.env.user.has_group("qms_core.group_qms_manager"):
            raise UserError(_("Only the assigned employee or a QMS Manager can acknowledge this document."))
        self.write({"status": "acknowledged", "acknowledged_on": fields.Datetime.now()})
        return True
