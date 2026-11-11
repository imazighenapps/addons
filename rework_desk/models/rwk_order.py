# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RwkOrder(models.Model):
    _name = "rwk.order"
    _description = "Rework Order"
    _inherit = ["mail.thread"]
    _order = "planned_on desc, id desc"

    name = fields.Char(
        required=True, copy=False, tracking=True,
        default=lambda self: _("New"),
        help="Reference of the rework order.")
    reject_id = fields.Many2one(
        "rwk.reject", string="Rejected Output", required=True,
        ondelete="cascade", index=True, tracking=True)
    quantity = fields.Float(
        string="Rework Quantity", required=True, default=1.0,
        tracking=True, help="Quantity to be reworked in this order.")
    planned_on = fields.Date(
        string="Planned On", required=True,
        default=fields.Date.context_today, tracking=True)
    done_on = fields.Date(
        string="Done On", readonly=True, copy=False, tracking=True)
    owner_id = fields.Many2one(
        "res.users", string="Owner", required=True,
        default=lambda self: self.env.user, tracking=True)
    instructions = fields.Text(
        string="Instructions",
        help="What must be done during the second pass.")
    state = fields.Selection(
        [("draft", "Draft"), ("planned", "Planned"),
         ("running", "Running"), ("done", "Done")],
        default="draft", required=True, tracking=True, index=True,
        copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "rwk.order") or _("RWK-%s") % fields.Date.context_today(
                    self).strftime("%Y%m%d")
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_(
                    "The rework quantity of %s must be above zero.", rec.name))

    @api.constrains("quantity", "reject_id")
    def _check_rework_limit(self):
        for rec in self:
            if rec.reject_id and rec.quantity > rec.reject_id.quantity:
                raise ValidationError(_(
                    "The rework quantity of %s cannot exceed the rejected "
                    "quantity.", rec.name))

    @api.constrains("planned_on", "done_on")
    def _check_dates(self):
        for rec in self:
            if rec.done_on and rec.planned_on and rec.done_on < rec.planned_on:
                raise ValidationError(_(
                    "The rework order %s cannot be done before it was planned.",
                    rec.name))

    def action_plan(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_(
                    "Only a draft rework order can be planned."))
            rec.state = "planned"
            if rec.reject_id.state == "open":
                rec.reject_id.state = "in_rework"
        return True

    def action_start(self):
        for rec in self:
            if rec.state != "planned":
                raise ValidationError(_(
                    "Only a planned rework order can be started."))
            rec.state = "running"
        return True

    def action_done(self):
        for rec in self:
            if rec.state != "running":
                raise ValidationError(_(
                    "Only a running rework order can be completed."))
            rec.write({
                "state": "done",
                "done_on": fields.Date.context_today(rec),
            })
            rec.message_post(body=_("Rework order completed."))
        return True
