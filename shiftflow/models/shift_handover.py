from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ShiftFlowHandover(models.Model):
    _name = "shiftflow.handover"
    _description = "Shift Handover"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(readonly=True, copy=False, default=lambda self: _("New"))
    outgoing_shift_id = fields.Many2one("shiftflow.shift", required=True, ondelete="cascade", index=True)
    incoming_shift_id = fields.Many2one("shiftflow.shift", ondelete="set null")
    company_id = fields.Many2one(related="outgoing_shift_id.company_id", store=True, index=True)
    prepared_by_id = fields.Many2one("res.users", readonly=True)
    prepared_at = fields.Datetime(readonly=True)
    accepted_by_id = fields.Many2one("res.users", readonly=True)
    accepted_at = fields.Datetime(readonly=True)
    rejection_reason = fields.Text(translate=True)
    state = fields.Selection([("draft", "Draft"), ("prepared", "Prepared"), ("waiting", "Waiting Acceptance"), ("accepted", "Accepted"), ("rejected", "Rejected")], default="draft", tracking=True)
    item_ids = fields.One2many("shiftflow.handover.item", "handover_id")
    summary = fields.Text(translate=True)
    item_count = fields.Integer(compute="_compute_item_count")

    @api.constrains("outgoing_shift_id", "incoming_shift_id")
    def _check_shift_pair(self):
        for rec in self:
            if rec.incoming_shift_id and rec.outgoing_shift_id.company_id != rec.incoming_shift_id.company_id:
                raise ValidationError(_("Outgoing and incoming shifts must belong to the same company."))
            if rec.incoming_shift_id and rec.outgoing_shift_id.team_id != rec.incoming_shift_id.team_id:
                raise ValidationError(_("Outgoing and incoming shifts must belong to the same team."))
            if rec.incoming_shift_id and rec.incoming_shift_id.start_datetime < rec.outgoing_shift_id.end_datetime:
                raise ValidationError(_("The incoming shift must start when or after the outgoing shift ends."))

    @api.depends("item_ids")
    def _compute_item_count(self):
        for rec in self: rec.item_count = len(rec.item_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New": vals["name"] = self.env["ir.sequence"].next_by_code("shiftflow.handover") or "New"
        records = super().create(vals_list)
        records._populate_items()
        return records

    def _populate_items(self, force=False):
        self.ensure_one()
        if self.item_ids and not force:
            return
        if force:
            self.item_ids.unlink()
        lines = []
        _sev_to_priority = {"low": "low", "medium": "normal", "high": "high", "critical": "critical"}
        for rec in self.outgoing_shift_id.incident_ids.filtered(lambda x: x.carry_over and x.state not in ("resolved", "cancelled")):
            lines.append((0, 0, {"item_type": "incident", "incident_id": rec.id, "description": rec.name, "priority": _sev_to_priority.get(rec.severity, "normal"), "carry_over": True}))
        for rec in self.outgoing_shift_id.task_ids.filtered(lambda x: x.carry_over and x.state not in ("done", "cancelled")):
            lines.append((0, 0, {"item_type": "task", "task_id": rec.id, "description": rec.name, "priority": "high" if rec.priority in ("urgent", "high") else "normal", "carry_over": True}))
        for rec in self.outgoing_shift_id.log_ids.filtered(lambda x: x.priority in ("high", "critical")):
            lines.append((0, 0, {"item_type": "log", "log_id": rec.id, "description": rec.name, "priority": rec.priority, "carry_over": True}))
        if lines:
            self.item_ids = lines
        self.summary = _("%s item(s) transferred from %s to %s.") % (len(lines), self.outgoing_shift_id.display_name, self.incoming_shift_id.display_name if self.incoming_shift_id else _("next shift"))

    def action_prepare(self):
        self.ensure_one()
        if self.state not in ("draft", "rejected"): raise UserError(_("Only draft or rejected handovers can be prepared."))
        self._populate_items(force=True)
        self.write({"state": "prepared", "prepared_by_id": self.env.user.id, "prepared_at": fields.Datetime.now(), "rejection_reason": False})
    def action_send(self):
        self.ensure_one()
        if self.state != "prepared":
            raise UserError(_("Prepare the handover before sending it for acceptance."))
        if not self.incoming_shift_id:
            raise UserError(_("Select an incoming shift before sending the handover."))
        self.state = "waiting"
        if self.incoming_shift_id.supervisor_id:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.incoming_shift_id.supervisor_id.id,
                summary=_("Shift handover awaiting acceptance"),
                note=_("Review and accept handover %s.") % self.display_name,
            )
    def action_accept(self):
        self.ensure_one()
        if self.state != "waiting":
            raise UserError(_("Only handovers waiting for acceptance can be accepted."))
        allowed = self.env.user.has_group("shiftflow.group_shiftflow_manager") or self.env.user == self.incoming_shift_id.supervisor_id or self.env.user == self.incoming_shift_id.team_id.manager_id
        if not allowed:
            raise UserError(_("Only the incoming shift supervisor, team manager, or a ShiftFlow Manager can accept this handover."))
        self.write({"state": "accepted", "accepted_by_id": self.env.user.id, "accepted_at": fields.Datetime.now()})
        self._create_carry_over_items()
        self.activity_unlink([self.env.ref("mail.mail_activity_data_todo").id])
    def action_reject(self):
        self.ensure_one()
        if self.state != "waiting": raise UserError(_("Only handovers waiting for acceptance can be rejected."))
        if not self.rejection_reason:
            raise UserError(_("Please provide a clarification or rejection reason before rejecting the handover."))
        self.write({"state": "rejected", "accepted_by_id": False, "accepted_at": False})

    def _create_carry_over_items(self):
        self.ensure_one()
        target = self.incoming_shift_id
        if not target: return
        for item in self.item_ids.filtered("carry_over"):
            if item.item_type == "incident" and item.incident_id and not item.incident_id.carried_to_id:
                new = item.incident_id.copy({"shift_id": target.id, "carried_from_id": item.incident_id.id, "carried_to_id": False, "state": "open"})
                item.incident_id.carried_to_id = new.id
            elif item.item_type == "task" and item.task_id and not item.task_id.carried_to_id:
                new = item.task_id.copy({"shift_id": target.id, "carried_from_id": item.task_id.id, "carried_to_id": False, "state": "open"})
                item.task_id.carried_to_id = new.id

class ShiftFlowHandoverItem(models.Model):
    _name = "shiftflow.handover.item"
    _description = "Handover Item"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    handover_id = fields.Many2one("shiftflow.handover", required=True, ondelete="cascade")
    item_type = fields.Selection([("incident", "Incident"), ("task", "Task"), ("log", "Log"), ("note", "Note")], required=True)
    incident_id = fields.Many2one("shiftflow.incident")
    task_id = fields.Many2one("shiftflow.task")
    log_id = fields.Many2one("shiftflow.log")
    description = fields.Text(required=True, translate=True)
    priority = fields.Selection([("low", "Low"), ("normal", "Normal"), ("high", "High"), ("critical", "Critical")], default="normal")
    carry_over = fields.Boolean(default=True)
    status_note = fields.Text(translate=True)
