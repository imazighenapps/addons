# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ChurnAction(models.Model):
    _name = "churn.action"
    _description = "Churn Save Action"
    _inherit = ["mail.thread"]
    _order = "planned_date asc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Save %s") % fields.Date.context_today(self))
    signal_id = fields.Many2one(
        "churn.signal", string="Signal", required=True,
        ondelete="cascade", index=True, tracking=True)
    partner_id = fields.Many2one(
        related="signal_id.partner_id", store=True, readonly=True)
    owner_id = fields.Many2one(
        "res.users", string="Owner", default=lambda self: self.env.user,
        tracking=True)
    planned_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    done_date = fields.Date(string="Done On", readonly=True, copy=False)
    outcome = fields.Selection(
        [("pending", "Pending"), ("contacted", "Contacted"),
         ("won_back", "Won Back"), ("no_answer", "No Answer")],
        default="pending", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("planned_date", "done_date")
    def _check_dates(self):
        for action in self:
            if action.done_date and action.done_date < action.planned_date:
                raise ValidationError(_(
                    "The done date of %s cannot come before the planned date.",
                    action.name))

    def action_done(self):
        for action in self:
            if action.outcome == "pending":
                raise ValidationError(_(
                    "Set an outcome before closing the action %s.",
                    action.name))
            action.write({"done_date": fields.Date.context_today(action)})
            action.message_post(body=_("The save action has been completed."))
        return True
