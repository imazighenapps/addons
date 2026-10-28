# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MaintEquipment(models.Model):
    _name = "maint.equipment"
    _description = "Equipment"
    _inherit = ["mail.thread"]
    _order = "code, id"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        required=True, index=True, tracking=True,
        help="Short internal reference of the equipment, for example "
             "EQ-CNC-01.")
    category = fields.Selection(
        [("machine", "Machine"), ("vehicle", "Vehicle"), ("tool", "Tool"),
         ("it", "IT Equipment"), ("other", "Other")],
        default="machine", required=True, tracking=True)
    location = fields.Char(
        help="Physical location of the equipment, for example Plant A - Bay 3.")
    serial_number = fields.Char(string="Serial Number")
    partner_id = fields.Many2one(
        "res.partner", string="Supplier / Owner",
        help="Supplier, lessor or owner of the equipment.")
    technician_id = fields.Many2one(
        "res.users", string="Responsible Technician",
        default=lambda self: self.env.user, tracking=True)
    purchase_date = fields.Date()
    warranty_end = fields.Date(string="Warranty End")
    criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium", required=True, tracking=True,
        help="How much a breakdown of this equipment hurts the production.")
    state = fields.Selection(
        [("running", "Running"), ("stopped", "Stopped"),
         ("retired", "Retired")],
        default="running", required=True, tracking=True, index=True)
    plan_ids = fields.One2many(
        "maint.plan", "equipment_id", string="Preventive Plans")
    request_ids = fields.One2many(
        "maint.request", "equipment_id", string="Maintenance Requests")
    open_request_count = fields.Integer(
        string="Open Requests", compute="_compute_request_stats")
    total_cost = fields.Monetary(
        string="Maintenance Cost", compute="_compute_request_stats",
        currency_field="currency_id",
        help="Total cost of the completed interventions.")
    last_intervention_date = fields.Date(
        string="Last Intervention", compute="_compute_request_stats")
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True,
        readonly=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "The equipment code must be unique per company.")

    @api.depends("request_ids.state", "request_ids.cost",
                 "request_ids.done_date")
    def _compute_request_stats(self):
        for equipment in self:
            open_requests = equipment.request_ids.filtered(
                lambda request: request.state in
                ("draft", "planned", "in_progress"))
            done_requests = equipment.request_ids.filtered(
                lambda request: request.state == "done")
            dates = [day for day in done_requests.mapped("done_date") if day]
            equipment.open_request_count = len(open_requests)
            equipment.total_cost = sum(done_requests.mapped("cost"))
            equipment.last_intervention_date = max(dates) if dates else False

    @api.constrains("purchase_date", "warranty_end")
    def _check_warranty(self):
        for equipment in self:
            if equipment.purchase_date and equipment.warranty_end \
                    and equipment.warranty_end < equipment.purchase_date:
                raise ValidationError(_(
                    "The warranty end date cannot be before the purchase "
                    "date."))

    def action_stop(self):
        for equipment in self:
            if equipment.state != "running":
                raise UserError(_(
                    "Only a running equipment can be stopped."))
            equipment.write({"state": "stopped"})
            equipment.message_post(body=_("Equipment stopped."))
        return True

    def action_start(self):
        for equipment in self:
            if equipment.state != "stopped":
                raise UserError(_(
                    "Only a stopped equipment can be started again."))
            equipment.write({"state": "running"})
            equipment.message_post(body=_("Equipment started again."))
        return True

    def action_retire(self):
        for equipment in self:
            if equipment.state == "retired":
                raise UserError(_("This equipment is already retired."))
            equipment.write({"state": "retired"})
            equipment.message_post(body=_(
                "Equipment retired: no new request can be opened."))
        return True

    def action_reinstate(self):
        for equipment in self:
            if equipment.state != "retired":
                raise UserError(_(
                    "Only a retired equipment can be reinstated."))
            equipment.write({"state": "running"})
            equipment.message_post(body=_("Equipment reinstated."))
        return True


class MaintPlan(models.Model):
    _name = "maint.plan"
    _description = "Preventive Maintenance Plan"
    _inherit = ["mail.thread"]
    _order = "next_date, id"

    name = fields.Char(required=True, tracking=True)
    equipment_id = fields.Many2one(
        "maint.equipment", string="Equipment", required=True,
        ondelete="cascade", index=True, tracking=True)
    period_days = fields.Integer(
        string="Period (days)", default=90, required=True,
        help="Number of days between two preventive interventions.")
    task = fields.Text(
        string="Preventive Task",
        help="What the technician has to do at each occurrence.")
    technician_id = fields.Many2one(
        "res.users", string="Technician",
        default=lambda self: self.env.user, tracking=True)
    last_date = fields.Date(string="Last Intervention")
    next_date = fields.Date(
        string="Next Due Date", compute="_compute_next_date", store=True,
        help="Last intervention plus the period. When the plan has no "
             "history yet, the plan is due today.")
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused")],
        default="active", required=True, tracking=True, index=True)
    request_ids = fields.One2many(
        "maint.request", "plan_id", string="Requests")
    request_count = fields.Integer(
        string="Requests", compute="_compute_request_count")

    @api.depends("last_date", "period_days")
    def _compute_next_date(self):
        today = fields.Date.context_today(self)
        for plan in self:
            if plan.last_date:
                plan.next_date = plan.last_date + timedelta(
                    days=plan.period_days or 0)
            else:
                plan.next_date = today

    @api.depends("request_ids")
    def _compute_request_count(self):
        for plan in self:
            plan.request_count = len(plan.request_ids)

    @api.constrains("period_days")
    def _check_period(self):
        for plan in self:
            if plan.period_days <= 0:
                raise ValidationError(_(
                    "The period must be at least one day."))

    def action_pause(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Only an active plan can be paused."))
            plan.write({"state": "paused"})
            plan.message_post(body=_("Preventive plan paused."))
        return True

    def action_resume(self):
        for plan in self:
            if plan.state != "paused":
                raise UserError(_("Only a paused plan can be resumed."))
            plan.write({"state": "active"})
            plan.message_post(body=_("Preventive plan resumed."))
        return True

    @api.model
    def _cron_generate_requests(self):
        today = fields.Date.context_today(self)
        plans = self.search([
            ("state", "=", "active"),
            ("next_date", "<=", today),
        ])
        created = 0
        for plan in plans:
            already_open = plan.request_ids.filtered(
                lambda request: request.type == "preventive"
                and request.state in ("draft", "planned", "in_progress")
                and request.request_date == today)
            if already_open:
                continue
            self.env["maint.request"].create({
                "equipment_id": plan.equipment_id.id,
                "plan_id": plan.id,
                "type": "preventive",
                "priority": "medium",
                "description": _(
                    "Preventive maintenance: %s", plan.name),
                "technician_id": plan.technician_id.id or False,
                "request_date": today,
                "scheduled_date": today,
                "state": "planned",
                "company_id": plan.equipment_id.company_id.id,
            })
            plan.last_date = today
            created += 1
        return created


class MaintRequest(models.Model):
    _name = "maint.request"
    _description = "Maintenance Request"
    _inherit = ["mail.thread"]
    _order = "request_date desc, id desc"

    name = fields.Char(default="/", required=True, copy=False, tracking=True)
    equipment_id = fields.Many2one(
        "maint.equipment", string="Equipment", required=True, index=True,
        tracking=True, domain=[("state", "!=", "retired")])
    plan_id = fields.Many2one(
        "maint.plan", string="Preventive Plan", ondelete="set null",
        tracking=True)
    type = fields.Selection(
        [("corrective", "Corrective"), ("preventive", "Preventive"),
         ("inspection", "Inspection")],
        default="corrective", required=True, tracking=True)
    priority = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium", required=True, tracking=True)
    description = fields.Text(required=True)
    reported_by = fields.Char(
        string="Reported By",
        help="Name of the person who reported the breakdown.")
    technician_id = fields.Many2one(
        "res.users", string="Technician", tracking=True)
    request_date = fields.Date(
        default=fields.Date.context_today, required=True, tracking=True)
    scheduled_date = fields.Date(tracking=True)
    done_date = fields.Date(string="Completion Date", tracking=True)
    duration_hours = fields.Float(
        string="Duration (hours)", default=0.0,
        help="Real intervention time, used as downtime.")
    cost = fields.Monetary(
        currency_field="currency_id", tracking=True,
        help="Parts, labour and subcontracting for this intervention.")
    currency_id = fields.Many2one(
        "res.currency", string="Currency",
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("planned", "Planned"),
         ("in_progress", "In Progress"), ("done", "Done"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "maint.request") or "/"
        return super().create(vals_list)

    @api.constrains("duration_hours")
    def _check_duration(self):
        for request in self:
            if request.duration_hours < 0:
                raise ValidationError(_(
                    "The intervention duration cannot be negative."))

    @api.constrains("cost")
    def _check_cost(self):
        for request in self:
            if request.cost < 0:
                raise ValidationError(_(
                    "The intervention cost cannot be negative."))

    def action_plan(self):
        for request in self:
            if request.state != "draft":
                raise UserError(_("Only a draft request can be planned."))
            if not request.scheduled_date:
                raise UserError(_(
                    "Set the scheduled date before planning the request."))
            request.write({"state": "planned"})
            request.message_post(body=_("Intervention planned."))
        return True

    def action_start(self):
        for request in self:
            if request.state != "planned":
                raise UserError(_(
                    "Only a planned request can be started."))
            request.write({"state": "in_progress"})
            request.message_post(body=_("Intervention started."))
        return True

    def action_done(self):
        for request in self:
            if request.state not in ("planned", "in_progress"):
                raise UserError(_(
                    "Only a planned or in-progress request can be "
                    "completed."))
            if request.duration_hours <= 0:
                raise UserError(_(
                    "Enter the intervention duration before completing "
                    "the request."))
            values = {"state": "done"}
            if not request.done_date:
                values["done_date"] = fields.Date.context_today(request)
            request.write(values)
            if request.plan_id:
                request.plan_id.last_date = request.done_date
            request.message_post(body=_(
                "Intervention completed in %(hours).2f hour(s) for "
                "%(cost).2f.", hours=request.duration_hours,
                cost=request.cost))
        return True

    def action_cancel(self):
        for request in self:
            if request.state == "done":
                raise UserError(_(
                    "A completed request cannot be cancelled."))
            if request.state == "cancelled":
                raise UserError(_("This request is already cancelled."))
            request.write({"state": "cancelled"})
            request.message_post(body=_("Request cancelled."))
        return True

    def action_reset(self):
        for request in self:
            if request.state != "cancelled":
                raise UserError(_(
                    "Only a cancelled request can be reset to draft."))
            request.write({"state": "draft", "done_date": False})
            request.message_post(body=_("Request reset to draft."))
        return True
