from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QmsMeasurementEquipment(models.Model):
    _name = "qms.measurement.equipment"
    _description = "QMS Measurement Equipment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "next_due_date, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('qms.measurement.equipment'), required=True, index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    equipment_type = fields.Char()
    manufacturer = fields.Char()
    serial_number = fields.Char()
    location = fields.Char()
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    measurement_range = fields.Char()
    accuracy = fields.Char()
    tolerance = fields.Char(string="Allowed Tolerance")
    required_uncertainty = fields.Char(string="Required Measurement Uncertainty")
    traceability_reference = fields.Char(string="Traceability Reference")
    calibration_provider = fields.Char(string="Calibration Provider")
    criticality = fields.Selection([("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium", required=True)
    impact_assessment_required = fields.Boolean(default=True)
    calibration_interval = fields.Integer(default=365, required=True)
    last_calibration_date = fields.Date()
    next_due_date = fields.Date(compute="_compute_next_due", store=True, index=True)
    state = fields.Selection([("draft", "Draft"), ("active", "Active"), ("due", "Due"), ("overdue", "Overdue"), ("out_of_service", "Out of Service")], default="draft", required=True, tracking=True)
    certificate_ids = fields.One2many("qms.measurement.calibration", "equipment_id", string="Calibration History")
    process_ids = fields.Many2many("qms.process", string="Processes")
    control_ids = fields.Many2many("qms.control", string="Controls")
    active = fields.Boolean(default=True)

    @api.depends("last_calibration_date", "calibration_interval")
    def _compute_next_due(self):
        for record in self:
            if record.last_calibration_date and record.calibration_interval > 0:
                record.next_due_date = fields.Date.add(record.last_calibration_date, days=record.calibration_interval)
            else:
                record.next_due_date = False

    @api.constrains("calibration_interval")
    def _check_interval(self):
        for record in self:
            if record.calibration_interval <= 0:
                raise ValidationError(_("The calibration interval must be greater than zero."))

    def action_activate(self):
        self.write({"state": "active"})
        return True

    def action_out_of_service(self):
        self.write({"state": "out_of_service"})
        return True

    @api.model
    def _cron_update_status(self):
        today = fields.Date.context_today(self)
        self.search([("state", "in", ["active", "due"]), ("next_due_date", "<", today)]).write({"state": "overdue"})
        self.search([("state", "=", "active"), ("next_due_date", "=", today)]).write({"state": "due"})
        return True


class QmsMeasurementCalibration(models.Model):
    _name = "qms.measurement.calibration"
    _description = "QMS Calibration Record"
    _order = "calibration_date desc, id desc"

    equipment_id = fields.Many2one("qms.measurement.equipment", required=True, ondelete="cascade", check_company=True)
    company_id = fields.Many2one("res.company", related="equipment_id.company_id", store=True, index=True, readonly=True)
    calibration_date = fields.Date(required=True, default=fields.Date.context_today)
    performed_by_id = fields.Many2one("res.partner", string="Performed By")
    result = fields.Selection([("pass", "Pass"), ("conditional", "Conditional Pass"), ("fail", "Fail")], default="pass", required=True)
    as_found = fields.Selection([("pass", "Pass"), ("fail", "Fail"), ("unknown", "Unknown")], default="unknown", required=True)
    as_left = fields.Selection([("pass", "Pass"), ("fail", "Fail"), ("unknown", "Unknown")], default="unknown", required=True)
    certificate_number = fields.Char()
    next_due_date = fields.Date()
    notes = fields.Text()
    reference_standard = fields.Char(string="Reference Standard")
    measurement_uncertainty = fields.Float(string="Measurement Uncertainty")
    decision_rule = fields.Text(string="Decision Rule")
    environmental_conditions = fields.Text(string="Environmental Conditions")
    impact_review = fields.Text(string="Impact Review")
    attachment_ids = fields.Many2many("ir.attachment", string="Certificates")

    @api.constrains("calibration_date", "next_due_date")
    def _check_dates(self):
        for record in self:
            if record.next_due_date and record.next_due_date < record.calibration_date:
                raise ValidationError(_("The next due date cannot be earlier than the calibration date."))

    def action_validate(self):
        for record in self:
            if record.result == "fail":
                record.equipment_id.write({"state": "out_of_service"})
                continue
            record.next_due_date = fields.Date.add(record.calibration_date, days=record.equipment_id.calibration_interval)
            record.equipment_id.write({"last_calibration_date": record.calibration_date, "state": "active"})
        return True
