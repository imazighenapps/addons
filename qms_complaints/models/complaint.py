from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QmsComplaint(models.Model):
    _name = "qms.complaint"
    _description = "QMS Customer Complaint"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _order = "received_at desc, id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.complaint"), required=True, index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one("res.partner", required=True, check_company=True, tracking=True)
    contact_email = fields.Char(related="partner_id.email", readonly=True)
    priority = fields.Selection([("0", "Low"), ("1", "Normal"), ("2", "High"), ("3", "Critical")], default="1", tracking=True)
    category = fields.Selection([
        ("product", "Product"), ("service", "Service"), ("delivery", "Delivery"),
        ("documentation", "Documentation"), ("communication", "Communication"), ("other", "Other")
    ], default="service", required=True)
    description = fields.Text(required=True)
    received_at = fields.Datetime(default=fields.Datetime.now, required=True, tracking=True)
    response_sla_hours = fields.Float(default=24.0, required=True)
    sla_deadline = fields.Datetime(compute="_compute_sla_deadline", store=True)
    sla_breached = fields.Boolean(compute="_compute_sla_breached", store=True, index=True)
    assigned_to_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    sla_escalation_hours = fields.Float(default=4.0, required=True)
    escalated_at = fields.Datetime(readonly=True)
    acknowledgement_deadline = fields.Datetime(compute="_compute_ack_deadline", store=True)
    state = fields.Selection([
        ("new", "New"), ("acknowledged", "Acknowledged"), ("investigating", "Investigating"),
        ("waiting_customer", "Waiting for Customer"), ("resolved", "Resolved"), ("closed", "Closed"), ("cancelled", "Cancelled")
    ], default="new", required=True, tracking=True, index=True)
    resolution = fields.Text()
    closed_at = fields.Datetime(readonly=True)
    satisfaction_score = fields.Integer()
    ncr_id = fields.Many2one("qms.ncr", readonly=True, copy=False)
    evidence_ids = fields.Many2many("qms.evidence", string="Evidence")

    @api.depends("received_at", "response_sla_hours")
    def _compute_sla_deadline(self):
        for record in self:
            if record.received_at:
                record.sla_deadline = fields.Datetime.add(record.received_at, hours=record.response_sla_hours or 0)
            else:
                record.sla_deadline = False

    @api.depends("received_at", "sla_escalation_hours")
    def _compute_ack_deadline(self):
        for record in self:
            record.acknowledgement_deadline = fields.Datetime.add(record.received_at, hours=record.sla_escalation_hours or 0) if record.received_at else False

    @api.depends("sla_deadline", "state")
    def _compute_sla_breached(self):
        now = fields.Datetime.now()
        for record in self:
            record.sla_breached = bool(record.sla_deadline and record.sla_deadline < now and record.state not in ("resolved", "closed", "cancelled"))

    @api.constrains("response_sla_hours", "sla_escalation_hours")
    def _check_sla(self):
        for record in self:
            if record.response_sla_hours <= 0 or record.sla_escalation_hours <= 0:
                raise ValidationError(_("SLA durations must be greater than zero."))

    def action_acknowledge(self):
        self.write({"state": "acknowledged"})
        return True

    def action_investigate(self):
        self.write({"state": "investigating"})
        return True

    def action_wait_customer(self):
        self.write({"state": "waiting_customer"})
        return True

    def action_resolve(self):
        for record in self:
            if not record.resolution:
                raise UserError(_("Record the resolution before closing the complaint."))
        self.write({"state": "resolved"})
        return True

    def action_close(self):
        for record in self:
            if record.state != "resolved":
                raise UserError(_("Only resolved complaints can be closed."))
        self.write({"state": "closed", "closed_at": fields.Datetime.now()})
        return True

    def action_escalate_to_ncr(self):
        self.ensure_one()
        if self.ncr_id:
            return {"type": "ir.actions.act_window", "res_model": "qms.ncr", "res_id": self.ncr_id.id, "view_mode": "form"}
        ncr = self.env["qms.ncr"].create({
            "name": self.name,
            "company_id": self.company_id.id,
            "source": "complaint",
            "severity": "major" if self.priority in ("2", "3") else "minor",
            "description": self.description,
        })
        self.ncr_id = ncr.id
        return {"type": "ir.actions.act_window", "res_model": "qms.ncr", "res_id": ncr.id, "view_mode": "form"}

    @api.model
    def _cron_sla_breach(self):
        overdue = self.search([
            ("sla_deadline", "<", fields.Datetime.now()),
            ("state", "not in", ["resolved", "closed", "cancelled"]),
            ("sla_breached", "=", True),
        ])
        for complaint in overdue:
            if not complaint.escalated_at:
                complaint.write({"escalated_at": fields.Datetime.now()})
            if complaint.assigned_to_id:
                existing = self.env["mail.activity"].search([
                    ("res_model", "=", complaint._name), ("res_id", "=", complaint.id),
                    ("user_id", "=", complaint.assigned_to_id.id), ("summary", "=", "Complaint SLA breached"),
                ], limit=1)
                if not existing:
                    complaint.activity_schedule("mail.mail_activity_data_todo", user_id=complaint.assigned_to_id.id, summary="Complaint SLA breached")
        return True
