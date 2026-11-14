# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ServiceChecklistTemplate(models.Model):
    _name = "service.checklist.template"
    _description = "Checklist Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name, id"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    description = fields.Text()
    item_ids = fields.One2many(
        "service.checklist.template.item", "template_id", string="Items",
        copy=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "A checklist template with this name already exists for this company."),
    ]

    def action_create_run(self):
        self.ensure_one()
        if not self.item_ids:
            raise UserError(_("Add at least one item to the template."))
        run = self.env["service.checklist.run"].create({
            "template_id": self.id,
            "name": self.name,
            "company_id": self.company_id.id,
        })
        lines = []
        for item in self.item_ids.sorted("sequence"):
            lines.append((0, 0, {
                "name": item.name,
                "sequence": item.sequence,
                "instruction": item.instruction,
            }))
        run.line_ids = lines
        return {
            "type": "ir.actions.act_window",
            "res_model": "service.checklist.run",
            "res_id": run.id,
            "view_mode": "form",
        }


class ServiceChecklistTemplateItem(models.Model):
    _name = "service.checklist.template.item"
    _description = "Checklist Template Item"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "service.checklist.template", required=True, ondelete="cascade",
        index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Item", required=True)
    instruction = fields.Text(string="Instruction")
    company_id = fields.Many2one(
        related="template_id.company_id", store=True, readonly=True)


class ServiceChecklistRun(models.Model):
    _name = "service.checklist.run"
    _description = "Checklist Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(string="Reference", required=True, tracking=True)
    template_id = fields.Many2one(
        "service.checklist.template", string="Template", tracking=True)
    job_ref = fields.Char(string="Job / Task Reference")
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    date_start = fields.Date(
        string="Start Date", default=fields.Date.context_today, tracking=True)
    date_done = fields.Date(string="Completion Date", readonly=True, copy=False)
    line_ids = fields.One2many(
        "service.checklist.run.line", "run_id", string="Items", copy=True)
    progress = fields.Float(
        compute="_compute_progress", string="Completion (%)", store=True)
    state = fields.Selection(
        [("draft", "In Progress"), ("done", "Completed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("line_ids.result")
    def _compute_progress(self):
        for rec in self:
            total = len(rec.line_ids)
            if not total:
                rec.progress = 0.0
                continue
            answered = len(rec.line_ids.filtered(lambda l: l.result != "todo"))
            rec.progress = 100.0 * answered / total

    @api.model_create_multi
    def create(self, vals_list):
        # allow template to pass explicit name; keep given name
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("A checklist run must contain at least one item."))
            pending = rec.line_ids.filtered(lambda l: l.result == "todo")
            if pending:
                raise UserError(
                    _("All items must have a result before completing the run."))
            rec.write({
                "state": "done",
                "date_done": fields.Date.context_today(self),
            })

    def action_cancel(self):
        for rec in self:
            if rec.state == "done":
                raise UserError(_("A completed checklist cannot be cancelled."))
            rec.state = "cancelled"

    def action_reopen(self):
        for rec in self:
            if rec.state == "done":
                rec.write({"state": "draft", "date_done": False})
            elif rec.state == "cancelled":
                rec.state = "draft"


class ServiceChecklistRunLine(models.Model):
    _name = "service.checklist.run.line"
    _description = "Checklist Run Item"
    _order = "run_id, sequence, id"

    run_id = fields.Many2one(
        "service.checklist.run", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Item", required=True)
    instruction = fields.Text(string="Instruction")
    result = fields.Selection(
        [("todo", "To Do"), ("done", "Done"), ("failed", "Failed"),
         ("na", "Not Applicable")],
        string="Result", default="todo", required=True)
    note = fields.Char(string="Note")
    company_id = fields.Many2one(
        related="run_id.company_id", store=True, readonly=True)
