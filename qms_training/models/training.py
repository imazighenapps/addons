from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QmsTrainingCourse(models.Model):
    _name = "qms.training.course"
    _description = "QMS Training Course"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.training.course"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    course_type = fields.Selection([
        ("induction", "Induction"),
        ("procedure", "Procedure Training"),
        ("quality", "Quality"),
        ("safety", "Safety"),
        ("compliance", "Compliance"),
        ("technical", "Technical"),
        ("other", "Other"),
    ], default="quality", required=True)
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    validity_days = fields.Integer(string="Validity (days)", default=365)
    description = fields.Html()
    requirement_ids = fields.Many2many("qms.requirement", "qms_training_course_requirement_rel", "course_id", "requirement_id", string="Requirements")
    document_ids = fields.Many2many("qms.document", "qms_training_course_document_rel", "course_id", "document_id", string="Controlled Documents")
    assignment_ids = fields.One2many("qms.training.assignment", "course_id", string="Assignments")
    assignment_count = fields.Integer(compute="_compute_counts", copy=False)
    active = fields.Boolean(default=True, tracking=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Training course codes must be unique per company.",
    )

    @api.depends("assignment_ids")
    def _compute_counts(self):
        for record in self:
            record.assignment_count = len(record.assignment_ids)

    @api.constrains("validity_days")
    def _check_validity(self):
        for record in self:
            if record.validity_days < 0:
                raise ValidationError(_("Training validity cannot be negative."))


class QmsTrainingAssignment(models.Model):
    _name = "qms.training.assignment"
    _description = "QMS Training Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "due_date, id"

    course_id = fields.Many2one("qms.training.course", required=True, ondelete="cascade", check_company=True)
    company_id = fields.Many2one("res.company", related="course_id.company_id", store=True, index=True, readonly=True)
    employee_id = fields.Many2one("res.users", string="Employee", required=True, check_company=True)
    assigned_date = fields.Date(default=fields.Date.context_today, required=True)
    due_date = fields.Date()
    completed_date = fields.Date()
    expiry_date = fields.Date()
    score = fields.Float(digits=(16, 2))
    minimum_score = fields.Float(default=0.0, digits=(16, 2))
    evidence_ids = fields.Many2many("qms.evidence", "qms_training_assignment_evidence_rel", "assignment_id", "evidence_id", string="Evidence")
    notes = fields.Text()
    state = fields.Selection([
        ("assigned", "Assigned"),
        ("completed", "Completed"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ], default="assigned", required=True, tracking=True, index=True)

    _employee_course_uniq = models.Constraint(
        "UNIQUE(course_id, employee_id, assigned_date)",
        "The same employee cannot receive the same course twice on the same date.",
    )

    @api.constrains("employee_id", "company_id")
    def _check_employee_company(self):
        for record in self:
            if record.employee_id and record.employee_id.company_id and record.employee_id.company_id != record.company_id:
                raise ValidationError(_("The trainee must belong to the training company."))

    @api.constrains("score", "minimum_score")
    def _check_scores(self):
        for record in self:
            if record.score < 0 or record.minimum_score < 0 or record.score > 100 or record.minimum_score > 100:
                raise ValidationError(_("Training scores must be between 0 and 100."))

    def action_mark_completed(self):
        for record in self:
            if not record.completed_date:
                record.completed_date = fields.Date.context_today(record)
            if record.score < record.minimum_score:
                raise UserError(_("The recorded score is below the required minimum score."))
            if record.course_id.validity_days:
                record.expiry_date = fields.Date.add(record.completed_date, days=record.course_id.validity_days)
            record.state = "completed"
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True

    @api.model
    def _cron_mark_expired(self):
        today = fields.Date.context_today(self)
        records = self.search([("state", "=", "completed"), ("expiry_date", "<", today)])
        records.write({"state": "expired"})
        return True


class QmsCompetencyRequirement(models.Model):
    _name = "qms.competency.requirement"
    _description = "QMS Competency Requirement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    role_name = fields.Char(string="Role / Function")
    level = fields.Selection([
        ("awareness", "Awareness"),
        ("basic", "Basic"),
        ("working", "Working"),
        ("advanced", "Advanced"),
        ("expert", "Expert"),
    ], default="working", required=True)
    mandatory = fields.Boolean(default=True)
    process_ids = fields.Many2many("qms.process", "qms_competency_process_rel", "competency_id", "process_id", string="Processes")
    course_ids = fields.Many2many("qms.training.course", "qms_competency_course_rel", "competency_id", "course_id", string="Required Courses")
    notes = fields.Text()
    active = fields.Boolean(default=True)


class QmsEmployeeCompetency(models.Model):
    _name = "qms.employee.competency"
    _description = "QMS Employee Competency"
    _order = "employee_id, requirement_id"

    employee_id = fields.Many2one("res.users", required=True, check_company=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    requirement_id = fields.Many2one("qms.competency.requirement", required=True, ondelete="restrict", check_company=True)
    achieved_level = fields.Selection([
        ("awareness", "Awareness"),
        ("basic", "Basic"),
        ("working", "Working"),
        ("advanced", "Advanced"),
        ("expert", "Expert"),
    ], default="awareness", required=True)
    assessment_date = fields.Date()
    expiry_date = fields.Date()
    evidence_ids = fields.Many2many("qms.evidence", "qms_employee_competency_evidence_rel", "competency_id", "evidence_id", string="Evidence")
    status = fields.Selection([
        ("provisional", "Provisional"),
        ("qualified", "Qualified"),
        ("expired", "Expired"),
        ("not_met", "Not Met"),
    ], default="provisional", required=True)

    @api.constrains("employee_id", "company_id")
    def _check_employee_company(self):
        for record in self:
            if record.employee_id and record.employee_id.company_id and record.employee_id.company_id != record.company_id:
                raise ValidationError(_("The employee must belong to the competency company."))
