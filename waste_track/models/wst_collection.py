# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WstCollection(models.Model):
    _name = "wst.collection"
    _description = "Waste Collection"
    _inherit = ["mail.thread"]
    _order = "collected_on desc, id desc"

    name = fields.Char(
        required=True, copy=False, tracking=True,
        default=lambda self: _("New"),
        help="Reference of the waste collection.")
    stream_id = fields.Many2one(
        "wst.stream", string="Waste Stream", required=True,
        ondelete="cascade", index=True, tracking=True)
    collected_on = fields.Date(
        string="Collected On", required=True,
        default=fields.Date.context_today, tracking=True)
    quantity = fields.Float(
        string="Quantity", required=True, default=1.0, tracking=True)
    unit_name = fields.Char(
        string="Unit", default="kg",
        help="Unit used to express the collected quantity.")
    contractor_ref = fields.Char(
        string="Contractor Reference", tracking=True,
        help="Reference provided by the contractor for this pickup.")
    receipt_no = fields.Char(
        string="Receipt Number", tracking=True, copy=False,
        help="Receipt or consignment note number filed for the collection.")
    filed_on = fields.Date(
        string="Filed On", readonly=True, copy=False, tracking=True)
    state = fields.Selection(
        [("planned", "Planned"), ("collected", "Collected"),
         ("filed", "Filed")],
        default="planned", required=True, tracking=True, index=True,
        copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "wst.collection") or _("WST-%s") % fields.Date.context_today(
                    self).strftime("%Y%m%d")
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_(
                    "The collected quantity of %s must be above zero.",
                    rec.name))

    @api.constrains("collected_on", "filed_on")
    def _check_dates(self):
        for rec in self:
            if rec.filed_on and rec.collected_on \
                    and rec.filed_on < rec.collected_on:
                raise ValidationError(_(
                    "Collection %s cannot be filed before it was collected.",
                    rec.name))

    def action_collect(self):
        for rec in self:
            if rec.state != "planned":
                raise ValidationError(_(
                    "Only a planned collection can be marked collected."))
            rec.state = "collected"
        return True

    def action_file(self):
        for rec in self:
            if rec.state != "collected":
                raise ValidationError(_(
                    "Only a collected record can be filed."))
            if not rec.receipt_no:
                raise ValidationError(_(
                    "Collection %s needs a receipt number before filing.",
                    rec.name))
            rec.write({
                "state": "filed",
                "filed_on": fields.Date.context_today(rec),
            })
            rec.message_post(body=_("Waste collection receipt filed."))
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "filed":
                raise ValidationError(_(
                    "A filed collection cannot be reset."))
            rec.state = "planned"
        return True
