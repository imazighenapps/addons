# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DutySlot(models.Model):
    _name = "duty.slot"
    _description = "Duty Slot"
    _inherit = ["mail.thread"]
    _order = "slot_start desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Duty %s")
        % fields.Date.context_today(self))
    roster_id = fields.Many2one(
        "duty.roster", string="Roster", required=True, ondelete="cascade",
        index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True,
        index=True)
    slot_start = fields.Date(required=True, tracking=True)
    slot_end = fields.Date(required=True, tracking=True)
    compensation = fields.Float(
        required=True, default=0.0,
        help="Compensation earned for serving this duty slot.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("slot_start", "slot_end")
    def _check_slot_dates(self):
        for slot in self:
            if slot.slot_end < slot.slot_start:
                raise ValidationError(_(
                    "The end date of slot %s cannot be before the start date.",
                    slot.name))

    @api.constrains("compensation")
    def _check_compensation(self):
        for slot in self:
            if slot.compensation < 0:
                raise ValidationError(_(
                    "Compensation for %s cannot be negative.", slot.name))

    @api.constrains("slot_start", "slot_end", "roster_id")
    def _check_within_roster(self):
        for slot in self:
            roster = slot.roster_id
            if roster and (slot.slot_start < roster.date_start
                           or slot.slot_end > roster.date_end):
                raise ValidationError(_(
                    "Slot %s must fall within the roster period of %s.",
                    slot.name, roster.name))
