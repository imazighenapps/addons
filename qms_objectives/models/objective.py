from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QmsObjective(models.Model):
    _name = "qms.objective"
    _description = "QMS Objective"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "deadline, code"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.objective"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    objective_type = fields.Selection([
        ("quality", "Quality"),
        ("customer", "Customer"),
        ("process", "Process"),
        ("supplier", "Supplier"),
        ("compliance", "Compliance"),
        ("people", "People"),
        ("other", "Other"),
    ], default="quality", required=True)
    process_id = fields.Many2one("qms.process", ondelete="restrict", check_company=True)
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    direction = fields.Selection([("increase", "Increase"), ("decrease", "Decrease"), ("target", "Reach Target")], default="target", required=True)
    unit = fields.Char()
    baseline_value = fields.Float(digits=(16, 2))
    target_value = fields.Float(digits=(16, 2))
    current_value = fields.Float(compute="_compute_current", store=True, digits=(16, 2))
    progress_percent = fields.Float(compute="_compute_progress", store=True, digits=(16, 2))
    start_date = fields.Date()
    deadline = fields.Date()
    description = fields.Text()
    measurement_ids = fields.One2many("qms.objective.measurement", "objective_id", string="Measurements")
    measurement_count = fields.Integer(compute="_compute_counts")
    status = fields.Selection([
        ("draft", "Draft"),
        ("on_track", "On Track"),
        ("at_risk", "At Risk"),
        ("delayed", "Delayed"),
        ("achieved", "Achieved"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ], default="draft", required=True, tracking=True, index=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Objective codes must be unique per company.",
    )

    @api.depends("measurement_ids.value", "measurement_ids.date")
    def _compute_current(self):
        for record in self:
            measurements = record.measurement_ids.sorted(key=lambda m: (m.date or fields.Date.today(), m.id))
            record.current_value = measurements[-1].value if measurements else record.baseline_value

    @api.depends("baseline_value", "target_value", "current_value", "direction")
    def _compute_progress(self):
        for record in self:
            baseline = record.baseline_value
            target = record.target_value
            current = record.current_value
            if record.direction == "increase":
                denominator = target - baseline
                progress = ((current - baseline) / denominator * 100.0) if denominator else (100.0 if current >= target else 0.0)
            elif record.direction == "decrease":
                denominator = baseline - target
                progress = ((baseline - current) / denominator * 100.0) if denominator else (100.0 if current <= target else 0.0)
            else:
                denominator = abs(target - baseline)
                progress = (100.0 if current == target else (max(0.0, 100.0 - abs(target - current) / denominator * 100.0) if denominator else 0.0))
            record.progress_percent = min(100.0, max(0.0, progress))

    @api.depends("measurement_ids")
    def _compute_counts(self):
        for record in self:
            record.measurement_count = len(record.measurement_ids)

    @api.constrains("start_date", "deadline")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.deadline and record.deadline < record.start_date:
                raise ValidationError(_("The objective deadline cannot be earlier than the start date."))

    def action_set_on_track(self):
        self.write({"status": "on_track"})
        return True

    def action_set_at_risk(self):
        self.write({"status": "at_risk"})
        return True

    def action_set_delayed(self):
        self.write({"status": "delayed"})
        return True

    def action_mark_achieved(self):
        self.write({"status": "achieved"})
        return True

    def action_mark_failed(self):
        self.write({"status": "failed"})
        return True

    def action_cancel(self):
        self.write({"status": "cancelled"})
        return True


class QmsObjectiveMeasurement(models.Model):
    _name = "qms.objective.measurement"
    _description = "QMS Objective Measurement"
    _order = "date desc, id desc"

    objective_id = fields.Many2one("qms.objective", required=True, ondelete="cascade", check_company=True)
    company_id = fields.Many2one("res.company", related="objective_id.company_id", store=True, index=True, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    value = fields.Float(required=True, digits=(16, 2))
    source = fields.Char()
    note = fields.Text()
