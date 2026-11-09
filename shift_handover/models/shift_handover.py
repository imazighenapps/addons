# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ShiftHandover(models.Model):
    _name = "shift.handover"
    _description = "Shift Handover"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _(
            "Handover %s", fields.Date.context_today(self)))
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True,
        index=True)
    shift = fields.Selection(
        [("morning", "Morning"), ("afternoon", "Afternoon"),
         ("night", "Night")],
        default="morning", required=True, tracking=True,
        help="Shift being handed over: the one that ends now.")
    responsible_id = fields.Many2one(
        "hr.employee", string="Responsible", required=True, tracking=True,
        help="Employee handing the shift over to the next team.")
    department_id = fields.Many2one(
        "hr.department", string="Department", tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    line_ids = fields.One2many(
        "shift.handover.line", "handover_id", string="Items", copy=True)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    open_count = fields.Integer(
        string="Open Items", compute="_compute_open_count", store=True,
        help="Items the next shift still has to deal with.")
    note = fields.Text()

    @api.depends("line_ids.resolved")
    def _compute_open_count(self):
        for handover in self:
            handover.open_count = len(handover.line_ids.filtered(
                lambda line: not line.resolved))

    def action_done(self):
        for handover in self:
            if not handover.line_ids:
                raise UserError(_(
                    "Record at least one item before closing the handover "
                    "\"%s\": an empty handover teaches the next shift "
                    "nothing.", handover.name))
            if handover.state != "draft":
                raise UserError(_(
                    "Only a draft handover can be marked as done."))
            handover.state = "done"
            handover.message_post(body=_(
                "Handover closed with %(count)s item(s), %(open)s still open "
                "for the next shift.",
                count=len(handover.line_ids), open=handover.open_count))
        return True

    def action_reopen(self):
        for handover in self:
            if handover.state != "done":
                raise UserError(_(
                    "Only a handover marked as done can be reopened."))
            handover.state = "draft"
            handover.message_post(body=_(
                "Handover reopened by %s.", self.env.user.name))
        return True

    def action_cancel(self):
        for handover in self:
            if handover.state == "done":
                raise UserError(_(
                    "The handover \"%s\" is done: it can no longer be "
                    "cancelled.", handover.name))
            if handover.state == "cancelled":
                raise UserError(_("This handover is already cancelled."))
            handover.state = "cancelled"
            handover.message_post(body=_(
                "Handover cancelled by %s.", self.env.user.name))
        return True


class ShiftHandoverLine(models.Model):
    _name = "shift.handover.line"
    _description = "Shift Handover Item"
    _order = "handover_id, sequence, id"

    handover_id = fields.Many2one(
        "shift.handover", string="Handover", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="handover_id.company_id", store=True, readonly=True)
    category = fields.Selection(
        [("incident", "Incident"), ("task", "Task"), ("stock", "Stock"),
         ("quality", "Quality"), ("other", "Other")],
        default="task", required=True,
        help="Nature of the point handed over to the next shift.")
    description = fields.Text(required=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium", required=True,
        help="How urgent the item is for the next team.")
    follow_up = fields.Boolean(
        default=False,
        help="The next shift has to act on this item.")
    resolved = fields.Boolean(default=False)
    resolved_date = fields.Datetime(copy=False)
    assigned_id = fields.Many2one(
        "hr.employee", string="Assigned To",
        help="Employee in charge of the follow-up.")

    def action_resolve(self):
        for line in self:
            if line.resolved:
                raise UserError(_("This item is already resolved."))
            line.write({
                "resolved": True,
                "resolved_date": fields.Datetime.now(),
            })
        return True

    def action_reopen(self):
        for line in self:
            if not line.resolved:
                raise UserError(_(
                    "Only a resolved item can be reopened."))
            line.write({"resolved": False, "resolved_date": False})
        return True
