# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class YieldRun(models.Model):
    _name = "yield.run"
    _description = "Production Yield Run"
    _inherit = ["mail.thread"]
    _order = "run_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    product_name = fields.Char(
        string="Product", required=True, tracking=True,
        help="Product or reference produced by this run.")
    run_date = fields.Date(
        string="Run Date", required=True,
        default=fields.Date.context_today, tracking=True)
    planned_qty = fields.Float(
        string="Planned Output", required=True, default=1.0,
        help="Quantity the production order should deliver.")
    actual_qty = fields.Float(
        string="Actual Output", required=True, default=0.0,
        help="Quantity really obtained at the end of the run.")
    loss_qty = fields.Float(
        string="Lost Quantity", compute="_compute_yield",
        store=True, tracking=True,
        help="Difference between planned and actual output.")
    yield_rate = fields.Float(
        string="Yield Rate (%)", compute="_compute_yield",
        store=True, tracking=True,
        help="Actual output as a percentage of the planned output.")
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    loss_ids = fields.One2many(
        "yield.loss", "run_id", string="Losses", copy=True)
    loss_count = fields.Integer(
        string="Loss Lines", compute="_compute_loss_count", store=True)
    line_loss_qty = fields.Float(
        string="Named Losses", compute="_compute_loss_count", store=True,
        help="Total quantity reported on the named loss lines.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("planned_qty", "actual_qty")
    def _compute_yield(self):
        for run in self:
            run.loss_qty = max(run.planned_qty - run.actual_qty, 0.0)
            run.yield_rate = (
                run.actual_qty / run.planned_qty * 100.0
                if run.planned_qty else 0.0)

    @api.depends("loss_ids.quantity")
    def _compute_loss_count(self):
        for run in self:
            run.loss_count = len(run.loss_ids)
            run.line_loss_qty = sum(run.loss_ids.mapped("quantity"))

    @api.constrains("planned_qty", "actual_qty")
    def _check_quantities(self):
        for run in self:
            if run.planned_qty <= 0:
                raise ValidationError(_(
                    "The planned output of %s must be above zero.",
                    run.name))
            if run.actual_qty < 0:
                raise ValidationError(_(
                    "The actual output of %s cannot be negative.",
                    run.name))
            if run.actual_qty > run.planned_qty:
                raise ValidationError(_(
                    "The actual output of %s cannot exceed the planned "
                    "output.", run.name))

    def action_start(self):
        for run in self:
            if run.state != "draft":
                raise UserError(_("Only a draft run can be started."))
            run.state = "running"
            run.message_post(body=_("Run started."))
        return True

    def action_close(self):
        for run in self:
            if run.state != "running":
                raise UserError(_("Only a running run can be closed."))
            run.state = "closed"
            run.message_post(body=_(
                "Run closed with a yield of %(rate).1f%%.",
                rate=run.yield_rate))
        return True

    def action_reset(self):
        for run in self:
            if run.state != "closed":
                raise UserError(_("Only a closed run can be reset to draft."))
            run.state = "draft"
            run.message_post(body=_("Run reset to draft."))
        return True

    def write(self, vals):
        if {"planned_qty", "actual_qty", "product_name"} & set(vals):
            for run in self:
                if run.state == "closed":
                    raise UserError(_(
                        "The output of the closed run \"%s\" can no longer "
                        "be changed. Reset it to draft first.", run.name))
        return super().write(vals)
