# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CleaningLog(models.Model):
    _name = "cleaning.log"
    _description = "Cleaning Log Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_planned desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    area = fields.Char(string="Area / Location", required=True, tracking=True)
    task = fields.Char(string="Task", required=True, tracking=True)
    date_planned = fields.Date(
        string="Planned Date", required=True, default=fields.Date.context_today, tracking=True)
    date_done = fields.Datetime(string="Completed On", tracking=True)
    responsible_id = fields.Many2one("hr.employee", string="Responsible", tracking=True)
    state = fields.Selection(
        [("planned", "Planned"), ("done", "Done"), ("missed", "Missed"), ("cancelled", "Cancelled")],
        default="planned", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("cleaning.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Cleaning Log",
                        "code": "cleaning.log",
                        "prefix": "CLN/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_done(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError(_("Only a planned task can be marked done."))
            rec.write({"state": "done", "date_done": rec.date_done or fields.Datetime.now()})

    def action_missed(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError(_("Only a planned task can be marked missed."))
            rec.state = "missed"

    def action_cancel(self):
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError(_("This task cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state == "planned":
                raise UserError(_("This task is already planned."))
            rec.write({"state": "planned", "date_done": False})
