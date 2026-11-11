# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LabelJob(models.Model):
    _name = "label.job"
    _description = "Label Print Job"
    _inherit = ["mail.thread"]
    _order = "print_date desc, id desc"

    name = fields.Char(
        required=True, copy=False, default="New", tracking=True,
        help="Reference of the print job.")
    template_id = fields.Many2one(
        "label.template", required=True, ondelete="restrict",
        tracking=True, index=True)
    label_type = fields.Selection(
        related="template_id.label_type", store=True, readonly=True)
    target_name = fields.Char(
        string="Target", required=True, tracking=True,
        help="Product, lot or location targeted by this print job.")
    quantity = fields.Integer(
        required=True, default=1, tracking=True,
        help="Number of labels requested.")
    print_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True,
        help="Date the labels were requested or printed.")
    state = fields.Selection(
        [("draft", "Draft"), ("printed", "Printed"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    printed_on = fields.Date(
        readonly=True, copy=False,
        help="Date the job was marked as printed.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "label.job") or _("LJ-%s") % fields.Date.context_today(self)
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s must be greater than zero.", record.name))

    def action_print(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only draft jobs can be printed."))
            record.write({
                "state": "printed",
                "printed_on": fields.Date.context_today(record),
            })
            record.message_post(body=_("Label job printed."))
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "printed":
                raise UserError(_("Printed jobs cannot be cancelled."))
            record.state = "cancelled"
            record.message_post(body=_("Label job cancelled."))
        return True

    def action_reset(self):
        for record in self:
            if record.state == "draft":
                raise UserError(_("Draft jobs cannot be reset."))
            record.write({"state": "draft", "printed_on": False})
            record.message_post(body=_("Label job reset to draft."))
        return True
