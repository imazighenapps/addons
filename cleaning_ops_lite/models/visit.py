# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class CleaningVisit(models.Model):
    _name = "cleaning.visit"
    _description = "Cleaning Visit"
    _inherit = ["mail.thread"]
    _order = "scheduled_date desc, id desc"

    name = fields.Char(default="/", copy=False, readonly=True)
    site_id = fields.Many2one("cleaning.site", required=True,
                             ondelete="restrict")
    plan_id = fields.Many2one("cleaning.plan", ondelete="set null")
    agent_id = fields.Many2one("cleaning.agent", required=True,
                               ondelete="restrict")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    scheduled_date = fields.Date(default=fields.Date.today, required=True)
    check_in = fields.Datetime(readonly=True)
    check_out = fields.Datetime(readonly=True)
    duration_hours = fields.Float(compute="_compute_duration", store=True)
    qc_score = fields.Float(string="Quality Score (%)", default=100.0)
    qc_notes = fields.Text(string="Quality Notes")
    checklist = fields.Text(
        string="Checklist Result",
        help="One item per line, e.g. 'Reception OK; WC cleaned; glass done'.")
    price = fields.Float(compute="_compute_price", store=True, readonly=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    invoice_id = fields.Many2one("account.move", string="Invoice",
                                 ondelete="set null", readonly=True)
    state = fields.Selection(
        [("planned", "Planned"), ("in_progress", "In Progress"),
         ("done", "Completed"), ("invoiced", "Invoiced")],
        default="planned", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "cleaning.visit") or "/"
        return super().create(vals_list)

    @api.depends("check_in", "check_out")
    def _compute_duration(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                rec.duration_hours = round(
                    (rec.check_out - rec.check_in).total_seconds() / 3600.0, 2)
            else:
                rec.duration_hours = 0.0

    @api.depends("site_id")
    def _compute_price(self):
        for rec in self:
            rec.price = rec.site_id.visit_price()

    def action_check_in(self):
        for rec in self:
            if rec.state not in ("planned", "in_progress"):
                raise UserError("Only planned visits can be checked in.")
            if rec.check_in:
                raise UserError("This visit is already checked in.")
            rec.write({"check_in": fields.Datetime.now(), "state": "in_progress"})

    def action_check_out(self):
        for rec in self:
            if not rec.check_in:
                raise UserError("Check in before checking out.")
            if rec.state not in ("planned", "in_progress"):
                raise UserError("This visit is already finished.")
            rec.write({"check_out": fields.Datetime.now(), "state": "done"})

    def action_create_invoice(self):
        self.ensure_one()
        if self.state != "done":
            raise UserError("Only completed visits can be invoiced.")
        if self.invoice_id:
            raise UserError("This visit is already invoiced.")
        invoice = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.site_id.partner_id.id,
            "invoice_line_ids": [(0, 0, {
                "name": "Cleaning visit %s - %s" % (self.name, self.site_id.name),
                "quantity": 1.0,
                "price_unit": self.price,
            })],
        })
        self.invoice_id = invoice.id
        self.state = "invoiced"
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": invoice.id,
            "view_mode": "form",
        }

    @api.model
    def _cron_generate_visits(self):
        """Create the visits due today for every active plan."""
        today = fields.Date.today()
        created = 0
        plans = self.env["cleaning.plan"].search([("active", "=", True)])
        for plan in plans:
            if plan.next_date != today:
                continue
            existing = self.search_count(
                [("plan_id", "=", plan.id), ("scheduled_date", "=", today)])
            if existing:
                continue
            self.create({
                "site_id": plan.site_id.id,
                "plan_id": plan.id,
                "agent_id": plan.agent_id.id,
                "scheduled_date": today,
            })
            created += 1
        return created