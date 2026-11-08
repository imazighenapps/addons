# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class FieldWatchLog(models.Model):
    _name = "field.watch.log"
    _description = "Field Change"
    _inherit = ["mail.thread"]
    _order = "changed_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    rule_id = fields.Many2one("field.watch.rule", string="Rule")
    model_id = fields.Many2one(
        "ir.model", string="Model", required=True, ondelete="cascade")
    model_name = fields.Char(
        related="model_id.model", store=True, readonly=True)
    res_id = fields.Integer(string="Record ID", required=True)
    record_name = fields.Char()
    field_name = fields.Char(required=True)
    field_label = fields.Char()
    old_value = fields.Char()
    new_value = fields.Char()
    changed_by_id = fields.Many2one("res.users", string="Changed By")
    changed_date = fields.Datetime(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)
    message_id = fields.Many2one(
        "mail.message", string="Message", ondelete="set null")
    state = fields.Selection(
        [("new", "New"), ("reviewed", "Reviewed"), ("ignored", "Ignored")],
        default="new", required=True, tracking=True, index=True)
    note = fields.Text()

    _sql_constraints = [
        ('message_field_uniq', "unique(message_id, field_name)", "This change was already collected."),
    ]

    @api.depends("model_name", "field_name", "record_name")
    def _compute_name(self):
        for log in self:
            parts = [
                log.model_name or "",
                log.field_label or log.field_name or "",
                log.record_name or "",
            ]
            log.name = " / ".join(part for part in parts if part) \
                or _("Field change")

    def action_review(self):
        for log in self:
            log.state = "reviewed"
        return True

    def action_ignore(self):
        for log in self:
            log.state = "ignored"
        return True

    def action_reopen(self):
        for log in self:
            log.state = "new"
        return True
