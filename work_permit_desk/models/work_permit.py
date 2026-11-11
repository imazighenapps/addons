# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WorkPermit(models.Model):
    _name = "work.permit"
    _description = "Work Permit"
    _inherit = ["mail.thread"]
    _order = "start_on desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Permit %s")
        % fields.Date.context_today(self), tracking=True,
        help="Reference of the work permit.")
    contractor = fields.Char(
        required=True, tracking=True,
        help="Name of the contractor or company performing the work.")
    area = fields.Char(
        string="Site Area", required=True, tracking=True,
        help="Area or zone where the intervention takes place.")
    work_type = fields.Selection(
        [("general", "General"), ("hot", "Hot Work"),
         ("electrical", "Electrical"), ("confined", "Confined Space"),
         ("height", "Work at Height")],
        default="general", required=True, tracking=True)
    start_on = fields.Datetime(
        string="Valid From", required=True,
        default=fields.Datetime.now, tracking=True)
    end_on = fields.Datetime(
        string="Valid Until", required=True, tracking=True)
    is_active_now = fields.Boolean(
        string="Valid Now", compute="_compute_active_flags", store=True,
        help="True when the permit is authorised and currently valid.")
    is_expired = fields.Boolean(
        string="Expired", compute="_compute_active_flags", store=True,
        help="True when the permit has passed its validity end.")
    state = fields.Selection(
        [("draft", "Draft"), ("authorised", "Authorised"),
         ("closed", "Closed"), ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    closed_on = fields.Datetime(
        string="Closed On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    description = fields.Text(help="Scope of the intervention.")
    note = fields.Text()

    @api.depends("state", "start_on", "end_on")
    def _compute_active_flags(self):
        now = fields.Datetime.now()
        for permit in self:
            valid_window = bool(
                permit.start_on and permit.end_on
                and permit.start_on <= now <= permit.end_on)
            permit.is_active_now = bool(
                permit.state == "authorised" and valid_window)
            permit.is_expired = bool(
                permit.end_on and permit.end_on < now
                and permit.state in ("authorised", "draft"))

    @api.constrains("start_on", "end_on")
    def _check_dates(self):
        for permit in self:
            if permit.start_on and permit.end_on \
                    and permit.end_on < permit.start_on:
                raise ValidationError(_(
                    "The end of permit %s cannot come before its start.",
                    permit.name))

    def action_authorise(self):
        for permit in self:
            if permit.state != "draft":
                raise ValidationError(_(
                    "Only a draft permit can be authorised."))
            permit.write({"state": "authorised"})
            permit.message_post(body=_(
                "The work permit has been authorised."))
        return True

    def action_close(self):
        for permit in self:
            if permit.state != "authorised":
                raise ValidationError(_(
                    "Only an authorised permit can be closed."))
            permit.write({
                "state": "closed",
                "closed_on": fields.Datetime.now(),
            })
            permit.message_post(body=_(
                "The work permit has been closed."))
        return True

    def action_cancel(self):
        for permit in self:
            if permit.state == "closed":
                raise ValidationError(_(
                    "A closed permit cannot be cancelled."))
            permit.write({"state": "cancelled"})
            permit.message_post(body=_(
                "The work permit has been cancelled."))
        return True
