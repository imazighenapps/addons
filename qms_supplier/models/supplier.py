from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QmsSupplier(models.Model):
    _name = "qms.supplier"
    _description = "QMS Supplier Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", required=True, ondelete="restrict", check_company=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    qualification_status = fields.Selection([
        ("draft", "Draft"),
        ("qualified", "Qualified"),
        ("probation", "Probation"),
        ("suspended", "Suspended"),
        ("disqualified", "Disqualified"),
    ], default="draft", required=True, tracking=True)
    risk_level = fields.Selection([
        ("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical"),
    ], default="medium", required=True, tracking=True)
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    review_date = fields.Date()
    notes = fields.Text()
    certificate_ids = fields.One2many("qms.supplier.certificate", "supplier_id", string="Certificates")
    evaluation_ids = fields.One2many("qms.supplier.evaluation", "supplier_id", string="Evaluations")
    latest_score = fields.Float(compute="_compute_latest_score", digits=(16, 2), copy=False)
    latest_evaluation_date = fields.Date(compute="_compute_latest_score", copy=False)
    certificate_count = fields.Integer(compute="_compute_counts", copy=False)
    evaluation_count = fields.Integer(compute="_compute_counts", copy=False)

    _partner_company_uniq = models.Constraint(
        "UNIQUE(partner_id, company_id)",
        "A supplier profile already exists for this company.",
    )

    @api.depends("evaluation_ids.overall_score", "evaluation_ids.evaluation_date")
    def _compute_latest_score(self):
        for record in self:
            latest = record.evaluation_ids.sorted(key=lambda e: (e.evaluation_date or fields.Date.today(), e.id), reverse=True)[:1]
            record.latest_score = latest.overall_score if latest else 0.0
            record.latest_evaluation_date = latest.evaluation_date if latest else False

    @api.depends("certificate_ids", "evaluation_ids")
    def _compute_counts(self):
        for record in self:
            record.certificate_count = len(record.certificate_ids)
            record.evaluation_count = len(record.evaluation_ids)

    @api.constrains("partner_id", "company_id")
    def _check_partner_company(self):
        for record in self:
            if record.partner_id.company_id and record.partner_id.company_id != record.company_id:
                raise ValidationError(_("The supplier contact must belong to the supplier company."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") and vals.get("partner_id"):
                vals["name"] = self.env["res.partner"].browse(vals["partner_id"]).name
        return super().create(vals_list)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id and not self.name:
            self.name = self.partner_id.name

    def action_qualify(self):
        self.write({"qualification_status": "qualified"})
        return True

    def action_suspend(self):
        self.write({"qualification_status": "suspended"})
        return True

    def action_requalify(self):
        self.write({"qualification_status": "qualified"})
        return True


class QmsSupplierCertificate(models.Model):
    _name = "qms.supplier.certificate"
    _description = "QMS Supplier Certificate"
    _order = "expiry_date, name"

    name = fields.Char(required=True)
    supplier_id = fields.Many2one("qms.supplier", required=True, ondelete="cascade", check_company=True)
    company_id = fields.Many2one("res.company", related="supplier_id.company_id", store=True, index=True, readonly=True)
    certificate_number = fields.Char()
    issuing_body_id = fields.Many2one("res.partner", string="Issuing Body")
    standard_id = fields.Many2one("qms.standard", string="Standard", check_company=True)
    issue_date = fields.Date()
    expiry_date = fields.Date()
    status = fields.Selection([
        ("draft", "Draft"), ("active", "Active"), ("expiring", "Expiring"),
        ("expired", "Expired"), ("superseded", "Superseded"),
    ], default="draft", required=True)
    notes = fields.Text()
    attachment_ids = fields.Many2many("ir.attachment", "qms_supplier_certificate_attachment_rel", "certificate_id", "attachment_id", string="Files")

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        for record in self:
            if record.issue_date and record.expiry_date and record.expiry_date < record.issue_date:
                raise ValidationError(_("The certificate expiry date cannot be earlier than the issue date."))

    @api.model
    def _cron_update_status(self):
        today = fields.Date.context_today(self)
        threshold = fields.Date.add(today, days=60)
        self.search([("status", "in", ["active", "expiring"]), ("expiry_date", "<", today)]).write({"status": "expired"})
        self.search([("status", "=", "active"), ("expiry_date", ">=", today), ("expiry_date", "<=", threshold)]).write({"status": "expiring"})
        return True


class QmsSupplierEvaluation(models.Model):
    _name = "qms.supplier.evaluation"
    _description = "QMS Supplier Evaluation"
    _order = "evaluation_date desc, id desc"

    supplier_id = fields.Many2one("qms.supplier", required=True, ondelete="cascade", check_company=True)
    company_id = fields.Many2one("res.company", related="supplier_id.company_id", store=True, index=True, readonly=True)
    evaluation_date = fields.Date(default=fields.Date.context_today, required=True)
    evaluator_id = fields.Many2one("res.users", default=lambda self: self.env.user, required=True, check_company=True)
    quality_score = fields.Float(required=True, default=0, digits=(16, 2))
    delivery_score = fields.Float(required=True, default=0, digits=(16, 2))
    responsiveness_score = fields.Float(required=True, default=0, digits=(16, 2))
    compliance_score = fields.Float(required=True, default=0, digits=(16, 2))
    overall_score = fields.Float(compute="_compute_overall_score", store=True, digits=(16, 2))
    conclusion = fields.Selection([
        ("approve", "Approved"), ("conditional", "Conditional"), ("improve", "Improvement Required"),
    ], default="conditional", required=True)
    notes = fields.Text()

    @api.depends("quality_score", "delivery_score", "responsiveness_score", "compliance_score")
    def _compute_overall_score(self):
        for record in self:
            record.overall_score = (record.quality_score + record.delivery_score + record.responsiveness_score + record.compliance_score) / 4.0

    @api.constrains("quality_score", "delivery_score", "responsiveness_score", "compliance_score")
    def _check_scores(self):
        for record in self:
            if any(value < 0 or value > 100 for value in (record.quality_score, record.delivery_score, record.responsiveness_score, record.compliance_score)):
                raise ValidationError(_("Supplier scores must be between 0 and 100."))
