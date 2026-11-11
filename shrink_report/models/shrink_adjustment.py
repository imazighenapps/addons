# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ShrinkAdjustment(models.Model):
    _name = "shrink.adjustment"
    _description = "Shrinkage Adjustment"
    _inherit = ["mail.thread"]
    _order = "adjustment_date desc, id desc"

    name = fields.Char(
        required=True, copy=False, default="New", tracking=True,
        help="Reference of the shrinkage adjustment entry.")
    product_name = fields.Char(
        string="Product", required=True, tracking=True,
        help="Product affected by the adjustment.")
    location_name = fields.Char(
        string="Location", required=True, tracking=True,
        help="Warehouse location where the loss was observed.")
    reason = fields.Selection(
        [("damage", "Damage"), ("theft", "Theft"),
         ("count_error", "Count Error"), ("expiry", "Expiry"),
         ("other", "Other")],
        default="other", required=True, tracking=True,
        help="Reason that explains the shrinkage.")
    adjustment_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True,
        help="Date the shrinkage was recorded.")
    quantity = fields.Float(
        required=True, default=1.0, tracking=True,
        help="Quantity lost in the adjustment.")
    unit_cost = fields.Monetary(
        required=True, currency_field="currency_id", tracking=True,
        help="Unit cost used to value the loss.")
    loss_value = fields.Monetary(
        string="Loss Value", currency_field="currency_id",
        compute="_compute_loss_value", store=True,
        help="Total loss value computed from quantity and unit cost.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("closed", "Closed")],
        default="draft", required=True, tracking=True, index=True)
    closed_on = fields.Date(
        string="Closed On", readonly=True, copy=False,
        help="Date the adjustment was closed.")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)

    @api.depends("quantity", "unit_cost")
    def _compute_loss_value(self):
        for record in self:
            record.loss_value = record.quantity * record.unit_cost

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "shrink.adjustment") or _("SW-%s") % fields.Date.context_today(self)
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s must be greater than zero.", record.name))

    @api.constrains("unit_cost")
    def _check_unit_cost(self):
        for record in self:
            if record.unit_cost < 0:
                raise ValidationError(_(
                    "The unit cost of %s cannot be negative.", record.name))

    def action_confirm(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only draft adjustments can be confirmed."))
            record.state = "confirmed"
            record.message_post(body=_("Shrinkage adjustment confirmed."))
        return True

    def action_close(self):
        for record in self:
            if record.state != "confirmed":
                raise UserError(_("Only confirmed adjustments can be closed."))
            record.write({
                "state": "closed",
                "closed_on": fields.Date.context_today(record),
            })
            record.message_post(body=_("Shrinkage adjustment closed."))
        return True

    def action_reset(self):
        for record in self:
            if record.state == "draft":
                raise UserError(_("Draft adjustments cannot be reset."))
            record.write({"state": "draft", "closed_on": False})
            record.message_post(body=_("Shrinkage adjustment reset to draft."))
        return True
