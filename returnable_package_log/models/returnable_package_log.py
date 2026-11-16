# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ReturnablePackageLog(models.Model):
    _name = "returnable.package.log"
    _description = "Returnable Packaging Movement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "movement_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, index=True,
        tracking=True)
    package_type = fields.Selection(
        [("pallet", "Pallet"), ("crate", "Crate"),
         ("box", "Box"), ("container", "Container")],
        required=True, default="pallet", tracking=True)
    quantity = fields.Integer(default=1, required=True)
    movement_type = fields.Selection(
        [("out", "Sent Out"), ("in", "Returned In")],
        required=True, default="out", tracking=True)
    movement_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    due_date = fields.Date(tracking=True)
    return_date = fields.Date()
    deposit_amount = fields.Float(string="Deposit Amount")
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"), ("returned", "Returned"),
         ("lost", "Lost"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code(
                    "returnable.package.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_("Quantity must be positive."))

    @api.constrains("deposit_amount")
    def _check_deposit(self):
        for record in self:
            if record.deposit_amount < 0:
                raise ValidationError(_("Deposit amount cannot be negative."))

    @api.constrains("movement_date", "due_date", "return_date")
    def _check_dates(self):
        for record in self:
            if record.due_date and record.movement_date \
                    and record.due_date < record.movement_date:
                raise ValidationError(
                    _("The due date cannot be before the movement date."))
            if record.return_date and record.movement_date \
                    and record.return_date < record.movement_date:
                raise ValidationError(
                    _("The return date cannot be before the movement date."))

    def action_send(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft movement can be sent."))
            record.state = "sent"
        return True

    def action_return(self):
        for record in self:
            if record.state != "sent":
                raise UserError(_("Only a sent movement can be returned."))
            record.write({
                "state": "returned",
                "return_date": record.return_date
                or fields.Date.context_today(record),
            })
        return True

    def action_mark_lost(self):
        for record in self:
            if record.state != "sent":
                raise UserError(_("Only a sent movement can be marked lost."))
            record.state = "lost"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("returned", "lost", "cancelled"):
                raise UserError(
                    _("A returned, lost or cancelled movement cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled movement can be reset."))
            record.write({"state": "draft", "return_date": False})
        return True
