from odoo import api, fields, models, _

class ShiftFlowIncident(models.Model):
    _name = "shiftflow.incident"
    _description = "Operational Incident"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "started_at desc"

    name = fields.Char(required=True, translate=True)
    reference = fields.Char(readonly=True, copy=False, default=lambda self: _("New"))
    shift_id = fields.Many2one("shiftflow.shift", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="shift_id.company_id", store=True, index=True)
    started_at = fields.Datetime(required=True, default=fields.Datetime.now, tracking=True)
    resolved_at = fields.Datetime(readonly=True)
    severity = fields.Selection([("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], default="medium", required=True, tracking=True)
    state = fields.Selection([("open", "Open"), ("investigating", "Investigating"), ("monitoring", "Monitoring"), ("resolved", "Resolved"), ("cancelled", "Cancelled")], default="open", tracking=True)
    owner_id = fields.Many2one("res.users", string="Responsible", default=lambda self: self.env.user)
    description = fields.Text(required=True, translate=True)
    resolution = fields.Text(translate=True)
    carry_over = fields.Boolean(string="Carry to Next Shift", default=True)
    carried_from_id = fields.Many2one("shiftflow.incident", readonly=True, copy=False)
    carried_to_id = fields.Many2one("shiftflow.incident", readonly=True, copy=False)
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    alert_sent = fields.Boolean(copy=False, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("shiftflow.incident") or "New"
        return super().create(vals_list)

    def write(self, vals):
        if "severity" in vals and vals["severity"] == "critical":
            vals = dict(vals, alert_sent=False)
        return super().write(vals)

    def action_resolve(self):
        self.write({"state": "resolved", "resolved_at": fields.Datetime.now()})
        for incident in self:
            incident.activity_unlink([self.env.ref("mail.mail_activity_data_todo").id])
    def action_cancel(self):
        self.write({"state": "cancelled"})
    def action_reopen(self):
        self.write({"state": "open", "resolved_at": False})

    @api.model
    def _cron_critical_incident_alerts(self):
        incidents = self.search([("severity", "=", "critical"), ("state", "not in", ["resolved", "cancelled"]), ("alert_sent", "=", False)])
        template = self.env.ref("shiftflow.mail_template_critical_incident", raise_if_not_found=False)
        for incident in incidents:
            if template and incident.owner_id.email:
                template.send_mail(incident.id, force_send=False)
            if incident.owner_id:
                incident.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=incident.owner_id.id,
                    summary=_("Critical incident requires attention"),
                    note=_("Review %(reference)s: %(name)s") % {"reference": incident.reference, "name": incident.name},
                )
            incident.alert_sent = True
        return True
