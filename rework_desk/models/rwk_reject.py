# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RwkReject(models.Model):
    _name = "rwk.reject"
    _description = "Rejected Output"
    _inherit = ["mail.thread"]
    _order = "detected_on desc, id desc"

    name = fields.Char(
        required=True, copy=False, tracking=True,
        default=lambda self: _("New"),
        help="Reference of the rejected output record.")
    product_ref = fields.Char(
        string="Product", required=True, tracking=True,
        help="Product or lot that was rejected.")
    quantity = fields.Float(
        string="Rejected Quantity", required=True, default=1.0,
        tracking=True, help="Quantity of output rejected.")
    unit_name = fields.Char(
        string="Unit", default="Units",
        help="Unit used to express the rejected quantity.")
    reason = fields.Text(
        string="Reason", required=True,
        help="Why the output was rejected.")
    detected_on = fields.Date(
        string="Detected On", required=True,
        default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("in_rework", "In Rework"), ("closed", "Closed")],
        default="open", required=True, tracking=True, index=True, copy=False)
    order_ids = fields.One2many(
        "rwk.order", "reject_id", string="Rework Orders")
    order_count = fields.Integer(
        string="Rework Orders", compute="_compute_counts", store=True)
    done_order_count = fields.Integer(
        string="Done Orders", compute="_compute_counts", store=True)
    reworked_qty = fields.Float(
        string="Reworked Quantity", compute="_compute_counts", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("order_ids", "order_ids.state", "order_ids.quantity")
    def _compute_counts(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)
            done = rec.order_ids.filtered(lambda o: o.state == "done")
            rec.done_order_count = len(done)
            rec.reworked_qty = sum(done.mapped("quantity"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "rwk.reject") or _("REJ-%s") % fields.Date.context_today(
                    self).strftime("%Y%m%d")
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_(
                    "The rejected quantity of %s must be above zero.",
                    rec.name))

    def action_close(self):
        for rec in self:
            if rec.state == "closed":
                raise ValidationError(_(
                    "The rejection %s is already closed.", rec.name))
            if rec.done_order_count == 0:
                raise ValidationError(_(
                    "Rejection %s cannot be closed without a completed rework "
                    "order.", rec.name))
            rec.state = "closed"
            rec.message_post(body=_("Rejected output closed after rework."))
        return True
