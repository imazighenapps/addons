from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ShiftFlowShift(models.Model):
    _name = "shiftflow.shift"
    _description = "Operational Shift"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc"

    name = fields.Char(string="Shift Reference", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    date = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    start_datetime = fields.Datetime(required=True, tracking=True)
    end_datetime = fields.Datetime(required=True, tracking=True)
    team_id = fields.Many2one("shiftflow.team", required=True, tracking=True)
    supervisor_id = fields.Many2one("res.users", string="Supervisor", tracking=True, default=lambda self: self.env.user)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ("draft", "Draft"), ("active", "Active"), ("closing", "Closing"),
        ("closed", "Closed"), ("cancelled", "Cancelled")], default="draft", tracking=True)
    previous_shift_id = fields.Many2one("shiftflow.shift", readonly=True, copy=False)
    next_shift_id = fields.Many2one("shiftflow.shift", readonly=True, copy=False)
    handover_id = fields.Many2one("shiftflow.handover", readonly=True, copy=False)
    log_ids = fields.One2many("shiftflow.log", "shift_id")
    incident_ids = fields.One2many("shiftflow.incident", "shift_id")
    task_ids = fields.One2many("shiftflow.task", "shift_id")
    log_count = fields.Integer(compute="_compute_counts")
    incident_count = fields.Integer(compute="_compute_counts")
    task_count = fields.Integer(compute="_compute_counts")
    open_issue_count = fields.Integer(compute="_compute_counts")
    notes = fields.Text(translate=True)

    @api.depends("log_ids", "incident_ids", "task_ids", "incident_ids.state", "task_ids.state")
    def _compute_counts(self):
        for rec in self:
            rec.log_count = len(rec.log_ids)
            rec.incident_count = len(rec.incident_ids)
            rec.task_count = len(rec.task_ids)
            rec.open_issue_count = len(rec.incident_ids.filtered(lambda x: x.state not in ("resolved", "cancelled"))) + len(rec.task_ids.filtered(lambda x: x.state not in ("done", "cancelled")))

    @api.constrains("start_datetime", "end_datetime", "team_id", "company_id", "state")
    def _check_dates_and_overlap(self):
        for rec in self:
            if rec.end_datetime <= rec.start_datetime:
                raise ValidationError(_("The end time must be later than the start time."))
            if not rec.team_id or rec.state == "cancelled":
                continue
            overlap = self.search_count([
                ("id", "!=", rec.id),
                ("team_id", "=", rec.team_id.id),
                ("company_id", "=", rec.company_id.id),
                ("state", "!=", "cancelled"),
                ("start_datetime", "<", rec.end_datetime),
                ("end_datetime", ">", rec.start_datetime),
            ])
            if overlap:
                raise ValidationError(_("A shift already exists for this team during the selected time range."))


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("shiftflow.shift") or "New"
        records = super().create(vals_list)
        records._link_adjacent_shifts()
        return records

    def write(self, vals):
        res = super().write(vals)
        if {"start_datetime", "end_datetime", "team_id", "company_id"} & set(vals):
            self._link_adjacent_shifts()
        return res

    def _link_adjacent_shifts(self):
        for rec in self:
            if not rec.team_id:
                continue
            domain = [("id", "!=", rec.id), ("team_id", "=", rec.team_id.id), ("company_id", "=", rec.company_id.id), ("state", "!=", "cancelled")]
            rec.previous_shift_id = self.search(domain + [("end_datetime", "<=", rec.start_datetime)], order="end_datetime desc", limit=1)
            rec.next_shift_id = self.search(domain + [("start_datetime", ">=", rec.end_datetime)], order="start_datetime asc", limit=1)

    def action_start(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft shifts can be started."))
        self.state = "active"

    def action_prepare_closing(self):
        self.ensure_one()
        if self.state != "active":
            raise UserError(_("Only active shifts can be moved to closing."))
        self.state = "closing"

    def action_close(self):
        self.ensure_one()
        if self.state not in ("active", "closing"):
            raise UserError(_("Only active or closing shifts can be closed."))
        self.state = "closed"

    def action_cancel(self):
        self.ensure_one()
        if self.state == "closed":
            raise UserError(_("A closed shift cannot be cancelled."))
        self.state = "cancelled"

    def action_prepare_handover(self):
        self.ensure_one()
        if self.state not in ("closing", "closed"):
            raise UserError(_("Move the shift to Closing before preparing a handover."))
        handover = self.env["shiftflow.handover"].search([("outgoing_shift_id", "=", self.id)], limit=1)
        if not handover:
            handover = self.env["shiftflow.handover"].create({"outgoing_shift_id": self.id, "incoming_shift_id": self.next_shift_id.id or False})
        self.handover_id = handover
        return {"type": "ir.actions.act_window", "res_model": "shiftflow.handover", "view_mode": "form", "res_id": handover.id}

    @api.model
    def get_dashboard_data(self):
        company = self.env.company
        today = fields.Date.context_today(self)
        now = fields.Datetime.now()
        shifts = self.search([("company_id", "=", company.id), ("date", "=", today)])
        active = shifts.filtered(lambda s: s.state == "active")[:1]
        Incident = self.env["shiftflow.incident"]
        Task = self.env["shiftflow.task"]
        Handover = self.env["shiftflow.handover"]
        open_inc = Incident.search([("company_id", "=", company.id), ("state", "not in", ["resolved", "cancelled"])])
        open_tasks = Task.search([("company_id", "=", company.id), ("state", "not in", ["done", "cancelled"])])
        sev_defs = [("critical", "Critical", "red"), ("high", "High", "orange"),
                    ("medium", "Medium", "amber"), ("low", "Low", "green")]
        incidents_by_severity = [
            {"label": label, "value": len(open_inc.filtered(lambda r, _k=key: r.severity == _k)), "tone": tone}
            for key, label, tone in sev_defs
        ]
        state_defs = [("open", "Open", "blue"), ("in_progress", "In Progress", "violet")]
        tasks_by_state = [
            {"label": label, "value": len(open_tasks.filtered(lambda r, _k=key: r.state == _k)), "tone": tone}
            for key, label, tone in state_defs
        ]
        week_start = today - timedelta(days=6)
        activity = []
        for back in range(6, -1, -1):
            day = today - timedelta(days=back)
            day_next = day + timedelta(days=1)
            day_start = fields.Datetime.to_datetime(day)
            day_end = fields.Datetime.to_datetime(day_next)
            activity.append({
                "label": day.strftime("%a %d"),
                "shifts": self.search_count([("company_id", "=", company.id), ("date", "=", day)]),
                "incidents": Incident.search_count([
                    ("company_id", "=", company.id),
                    ("started_at", ">=", fields.Datetime.to_string(day_start)),
                    ("started_at", "<", fields.Datetime.to_string(day_end))]),
                "tasks": Task.search_count([
                    ("company_id", "=", company.id),
                    ("create_date", ">=", fields.Datetime.to_string(day_start)),
                    ("create_date", "<", fields.Datetime.to_string(day_end))]),
            })
        open_list = open_inc.sorted(key=lambda r: ({"critical": 0, "high": 1, "medium": 2, "low": 3}.get(r.severity, 4), r.started_at), reverse=False)[:6]
        overdue = Task.search([
            ("company_id", "=", company.id),
            ("state", "not in", ["done", "cancelled"]),
            ("deadline", "<", now)], order="deadline asc", limit=6)
        waiting = Handover.search([("company_id", "=", company.id), ("state", "=", "waiting")],
                                  order="prepared_at desc, id desc", limit=6)
        return {
            "current_shift": active.name if active else _("No active shift"),
            "current_team": active.team_id.name if active else "",
            "open_incidents": len(open_inc),
            "critical_incidents": len(open_inc.filtered(lambda r: r.severity == "critical")),
            "overdue_tasks": Task.search_count([
                ("company_id", "=", company.id),
                ("state", "not in", ["done", "cancelled"]), ("deadline", "<", now)]),
            "today_shifts": len(shifts),
            "waiting_handovers": len(waiting),
            "carry_over_items": self.env["shiftflow.handover.item"].search_count([
                ("handover_id.company_id", "=", company.id),
                ("carry_over", "=", True), ("handover_id.state", "in", ["prepared", "waiting"])]),
            "resolved_week": Incident.search_count([
                ("company_id", "=", company.id), ("state", "=", "resolved"),
                ("resolved_at", ">=", fields.Datetime.to_string(fields.Datetime.to_datetime(week_start)))]),
            "incidents_by_severity": incidents_by_severity,
            "tasks_by_state": tasks_by_state,
            "activity": activity,
            "open_incidents_list": [{
                "reference": r.reference or "", "name": r.name or "",
                "severity": dict(r._fields["severity"].selection).get(r.severity, ""),
                "shift": r.shift_id.display_name or "", "owner": r.owner_id.display_name or "",
            } for r in open_list],
            "overdue_tasks_list": [{
                "reference": r.reference or "", "name": r.name or "",
                "deadline": fields.Datetime.to_string(r.deadline)[:16] if r.deadline else "",
                "responsible": r.responsible_id.display_name or "",
            } for r in overdue],
            "waiting_handovers_list": [{
                "name": h.display_name or "",
                "outgoing": h.outgoing_shift_id.display_name or "",
                "incoming": h.incoming_shift_id.display_name or "",
            } for h in waiting],
        }
