# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CycleCountPlan(models.Model):
    _name = "cycle.count.plan"
    _description = "Cycle Count Plan"
    _inherit = ["mail.thread"]
    _order = "next_date, id"

    name = fields.Char(required=True, tracking=True)
    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Warehouse", required=True,
        default=lambda self: self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1))
    responsible_id = fields.Many2one(
        "res.users", string="Responsible",
        default=lambda self: self.env.user)
    frequency_days = fields.Integer(
        string="Frequency (days)", default=30, required=True)
    next_date = fields.Date(
        string="Next Count", default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("paused", "Paused")],
        default="draft", required=True, tracking=True)
    line_ids = fields.One2many(
        "cycle.count.plan.line", "plan_id", string="Products")
    product_count = fields.Integer(compute="_compute_product_count")
    last_session_id = fields.Many2one(
        "cycle.count.session", string="Last Session", readonly=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    @api.depends("line_ids")
    def _compute_product_count(self):
        for plan in self:
            plan.product_count = len(plan.line_ids)

    def action_start(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Add at least one product to the plan."))
        self.write({"state": "running"})
        return True

    def action_pause(self):
        self.write({"state": "paused"})
        return True

    def action_resume(self):
        self.write({"state": "running"})
        return True

    def _create_session(self):
        self.ensure_one()
        session = self.env["cycle.count.session"].create({
            "plan_id": self.id,
            "warehouse_id": self.warehouse_id.id,
            "responsible_id": self.responsible_id.id,
            "date": fields.Date.context_today(self),
        })
        session.action_start()
        return session

    def action_new_session(self):
        self.ensure_one()
        session = self._create_session()
        return {
            "type": "ir.actions.act_window",
            "name": _("Cycle Count Session"),
            "res_model": "cycle.count.session",
            "res_id": session.id,
            "view_mode": "form",
        }

    @api.model
    def _cron_create_sessions(self):
        today = fields.Date.context_today(self)
        plans = self.search([
            ("state", "=", "running"),
            ("next_date", "<=", today),
        ])
        for plan in plans:
            plan._create_session()


class CycleCountPlanLine(models.Model):
    _name = "cycle.count.plan.line"
    _description = "Cycle Count Plan Line"
    _order = "sequence, id"

    plan_id = fields.Many2one(
        "cycle.count.plan", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True)
    location_id = fields.Many2one(
        "stock.location", string="Location",
        help="Leave empty to use the stock location of the warehouse.")
    note = fields.Char()


class CycleCountSession(models.Model):
    _name = "cycle.count.session"
    _description = "Cycle Count Session"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    plan_id = fields.Many2one(
        "cycle.count.plan", string="Plan", ondelete="set null")
    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Warehouse", required=True)
    date = fields.Date(
        default=fields.Date.context_today, required=True, tracking=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible",
        default=lambda self: self.env.user)
    state = fields.Selection(
        [("draft", "Draft"), ("counting", "Counting"),
         ("review", "To Review"), ("done", "Done"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True)
    line_ids = fields.One2many(
        "cycle.count.line", "session_id", string="Count Lines")
    line_count = fields.Integer(compute="_compute_totals")
    counted_count = fields.Integer(compute="_compute_totals")
    total_difference = fields.Float(
        string="Quantity Variance", compute="_compute_totals")
    variance_value = fields.Monetary(
        string="Value Variance", compute="_compute_totals",
        currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)

    @api.depends("line_ids.difference", "line_ids.value_difference",
                 "line_ids.is_counted")
    def _compute_totals(self):
        for session in self:
            session.line_count = len(session.line_ids)
            session.counted_count = len(
                session.line_ids.filtered("is_counted"))
            session.total_difference = sum(
                session.line_ids.mapped("difference"))
            session.variance_value = sum(
                session.line_ids.mapped("value_difference"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "cycle.count.session") or "/"
        return super().create(vals_list)

    def action_start(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only a draft session can be started."))
        if not self.line_ids:
            if not self.plan_id or not self.plan_id.line_ids:
                raise UserError(_("The session has no product to count."))
            for line in self.plan_id.line_ids:
                location = line.location_id or self.warehouse_id.lot_stock_id
                self.env["cycle.count.line"].create({
                    "session_id": self.id,
                    "product_id": line.product_id.id,
                    "location_id": location.id,
                    "theoretical_qty": self._theoretical_qty(
                        line.product_id, location),
                })
        self.write({"state": "counting"})
        if self.plan_id and self.plan_id.state == "draft":
            self.plan_id.action_start()
        return True

    @api.model
    def _theoretical_qty(self, product, location):
        quants = self.env["stock.quant"].search([
            ("product_id", "=", product.id),
            ("location_id", "=", location.id),
        ])
        return sum(quants.mapped("quantity"))

    def action_finish(self):
        self.ensure_one()
        if self.state != "counting":
            raise UserError(_("Only a running session can be finished."))
        missing = self.line_ids.filtered(lambda line: not line.is_counted)
        if missing:
            raise UserError(
                _("%s line(s) are not counted yet. Count every line or "
                  "remove it from the session.") % len(missing))
        self.write({"state": "review"})
        return True

    def action_validate(self):
        self.ensure_one()
        if self.state != "review":
            raise UserError(_("Only a session to review can be validated."))
        for line in self.line_ids:
            if not line.is_counted or not line.difference:
                continue
            quant = self.env["stock.quant"].search([
                ("product_id", "=", line.product_id.id),
                ("location_id", "=", line.location_id.id),
                ("company_id", "=", line.session_id.company_id.id),
            ], limit=1)
            if not quant:
                quant = self.env["stock.quant"].create({
                    "product_id": line.product_id.id,
                    "location_id": line.location_id.id,
                    "quantity": line.theoretical_qty,
                    "company_id": line.session_id.company_id.id,
                })
            quant.inventory_quantity = line.counted_qty
            quant.action_apply_inventory()
            line.state = "adjusted"
        self.write({"state": "done"})
        if self.plan_id:
            plan = self.plan_id
            plan.write({
                "last_session_id": self.id,
                "next_date": fields.Date.context_today(self) + timedelta(
                    days=plan.frequency_days or 30),
            })
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True

    def action_reset(self):
        self.write({"state": "draft"})
        return True


class CycleCountLine(models.Model):
    _name = "cycle.count.line"
    _description = "Cycle Count Line"
    _order = "session_id, id"

    session_id = fields.Many2one(
        "cycle.count.session", required=True, ondelete="cascade",
        index=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True)
    location_id = fields.Many2one(
        "stock.location", string="Location", required=True)
    theoretical_qty = fields.Float(
        string="Theoretical", default=0.0, readonly=True)
    counted_qty = fields.Float(string="Counted", default=0.0)
    is_counted = fields.Boolean(string="Counted")
    difference = fields.Float(
        string="Variance", compute="_compute_difference", store=True)
    unit_cost = fields.Monetary(
        string="Unit Cost", compute="_compute_difference", store=True,
        currency_field="currency_id")
    value_difference = fields.Monetary(
        string="Value Variance", compute="_compute_difference", store=True,
        currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("pending", "Pending"), ("adjusted", "Adjusted")],
        default="pending")
    note = fields.Char()

    @api.depends("theoretical_qty", "counted_qty", "is_counted",
                 "product_id.standard_price")
    def _compute_difference(self):
        for line in self:
            if line.is_counted:
                line.difference = line.counted_qty - line.theoretical_qty
            else:
                line.difference = 0.0
            line.unit_cost = line.product_id.standard_price or 0.0
            line.value_difference = line.difference * line.unit_cost

    _unique_product = models.Constraint(
        "UNIQUE(session_id, product_id, location_id)",
        "A product can only appear once per location in a session.")
