# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class WarehouseZoneEntry(models.Model):
    _name = "warehouse_zone.entry"
    _description = "ZoneBook Entry"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True, default=lambda self: _("New"))
    partner_id = fields.Many2one("res.partner", string="Partner", tracking=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user, tracking=True)
    date_start = fields.Date(
        string="Date", default=fields.Date.context_today, required=True, tracking=True)
    date_end = fields.Date(string="End Date")
    amount = fields.Monetary(string="Amount", currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, required=True)
    line_ids = fields.One2many("warehouse_zone.item", "entry_id", string="Lines", copy=True)
    line_count = fields.Integer(compute="_compute_line_count", store=True)
    state = fields.Selection([
        ("draft", "Draft"), ("confirmed", "Confirmed"),
        ("done", "Done"), ("cancelled", "Cancelled"),
    ], default="draft", required=True, tracking=True, index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_end and rec.date_start and rec.date_end < rec.date_start:
                raise ValidationError(_("The end date cannot be before the start date."))

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only draft records can be confirmed."))
            rec.state = "confirmed"
        return True

    def action_done(self):
        for rec in self:
            if rec.state != "confirmed":
                raise UserError(_("Only confirmed records can be marked done."))
            rec.state = "done"
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state in ("done",):
                raise UserError(_("Done records cannot be cancelled."))
            rec.state = "cancelled"
        return True

    def action_draft(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only cancelled records can be reset to draft."))
            rec.state = "draft"
        return True
