# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CylinderCustody(models.Model):
    _name = "cylinder.custody"
    _description = "Cylinder Custody"
    _inherit = ["mail.thread"]
    _order = "received_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Custody %s")
        % fields.Date.context_today(self),
        help="Reference of the custody line, generated at creation.")
    cylinder_type_id = fields.Many2one(
        "cylinder.type", string="Cylinder Type", required=True,
        ondelete="cascade", index=True, tracking=True)
    supplier_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, tracking=True)
    received_qty = fields.Integer(
        string="Received", default=1, required=True,
        help="Number of cylinders received from the supplier.")
    returned_qty = fields.Integer(
        string="Returned", default=0, required=True, copy=False,
        help="Number of cylinders returned to the supplier.")
    on_site_qty = fields.Integer(
        string="On Site", compute="_compute_on_site_qty", store=True,
        help="Cylinders still on site, received minus returned.")
    received_on = fields.Date(
        string="Received On", required=True,
        default=fields.Date.context_today, tracking=True)
    returned_on = fields.Date(string="Returned On", readonly=True, copy=False)
    state = fields.Selection(
        [("open", "On Site"), ("closed", "Returned")],
        default="open", required=True, copy=False, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("received_qty", "returned_qty")
    def _compute_on_site_qty(self):
        for line in self:
            line.on_site_qty = line.received_qty - line.returned_qty

    @api.constrains("received_qty")
    def _check_received_qty(self):
        for line in self:
            if line.received_qty <= 0:
                raise ValidationError(_(
                    "The received quantity for %s must be above zero.",
                    line.cylinder_type_id.name))

    @api.constrains("returned_qty", "received_qty")
    def _check_returned_qty(self):
        for line in self:
            if line.returned_qty < 0:
                raise ValidationError(_(
                    "The returned quantity for %s cannot be negative.",
                    line.cylinder_type_id.name))
            if line.returned_qty > line.received_qty:
                raise ValidationError(_(
                    "The returned quantity for %s cannot exceed what was "
                    "received.", line.cylinder_type_id.name))

    @api.constrains("received_on", "returned_on")
    def _check_dates(self):
        for line in self:
            if line.returned_on and line.returned_on < line.received_on:
                raise ValidationError(_(
                    "The return date of %s cannot come before the received "
                    "date.", line.name))

    def action_return(self):
        for line in self:
            if line.state != "open":
                raise ValidationError(_(
                    "The custody line %s is already closed.", line.name))
            line.write({
                "state": "closed",
                "returned_qty": line.received_qty,
                "returned_on": fields.Date.context_today(line),
            })
            line.message_post(body=_(
                "All cylinders were returned to the supplier."))
        return True
