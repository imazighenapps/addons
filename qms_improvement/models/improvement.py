from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QmsImprovement(models.Model):
    _name = "qms.improvement"
    _description = "QMS Continuous Improvement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, target_date, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.improvement"), required=True, index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    improvement_type = fields.Selection([("kaizen", "Kaizen"), ("process", "Process Improvement"), ("cost", "Cost Reduction"), ("customer", "Customer Experience"), ("quality", "Quality Improvement"), ("other", "Other")], default="kaizen", required=True)
    source = fields.Selection([("audit", "Audit"), ("ncr", "NCR / CAPA"), ("complaint", "Complaint"), ("risk", "Risk Review"), ("objective", "Objective"), ("suggestion", "Suggestion"), ("other", "Other")], default="suggestion", required=True)
    description = fields.Text(required=True)
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    target_date = fields.Date()
    priority = fields.Selection([("0", "Low"), ("1", "Normal"), ("2", "High"), ("3", "Strategic")], default="1", required=True)
    baseline_value = fields.Float()
    target_value = fields.Float()
    actual_value = fields.Float()
    unit = fields.Char()
    expected_benefit = fields.Text()
    benefit_value = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)
    action_plan = fields.Text()
    lessons_learned = fields.Text()
    status = fields.Selection([("idea", "Idea"), ("approved", "Approved"), ("in_progress", "In Progress"), ("completed", "Completed"), ("standardized", "Standardized"), ("cancelled", "Cancelled")], default="idea", required=True, tracking=True)

    def action_approve(self):
        self.write({"status": "approved"})
        return True

    def action_start(self):
        self.write({"status": "in_progress"})
        return True

    def action_complete(self):
        for record in self:
            if not record.lessons_learned:
                raise UserError(_("Record lessons learned before completing the improvement."))
        self.write({"status": "completed"})
        return True

    def action_standardize(self):
        for record in self:
            if record.status != "completed":
                raise UserError(_("Complete the improvement before standardizing it."))
        self.write({"status": "standardized"})
        return True

    def action_cancel(self):
        self.write({"status": "cancelled"})
        return True


class QmsLessonLearned(models.Model):
    _name = "qms.lesson.learned"
    _description = "QMS Lesson Learned"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    date = fields.Date(default=fields.Date.context_today, required=True)
    source_model = fields.Char()
    source_reference = fields.Char()
    situation = fields.Text(required=True)
    learning = fields.Text(required=True)
    action_to_standardize = fields.Text()
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    shared = fields.Boolean(default=False)
    status = fields.Selection([
        ("draft", "Draft"), ("approved", "Approved"), ("shared", "Shared"), ("archived", "Archived")
    ], default="draft", required=True, tracking=True)
