# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UnitCheck(models.Model):
    _name = "unit.check"
    _description = "Unit Check"
    _inherit = ["mail.thread"]
    _order = "checked_on desc, id desc"

    name = fields.Char(
        string="Reference", required=True, copy=False,
        default=lambda self: _("New"), tracking=True)
    document_ref = fields.Char(
        string="Document", required=True, tracking=True,
        help="Order, receipt or bill reference where the slip was found.")
    product_name = fields.Char(string="Product", required=True, tracking=True)
    source = fields.Selection(
        [("order", "Order"), ("receipt", "Receipt"), ("bill", "Bill"),
         ("other", "Other")],
        default="order", required=True, tracking=True)
    expected_unit = fields.Char(string="Expected Unit", required=True)
    entered_unit = fields.Char(string="Entered Unit", required=True)
    quantity = fields.Float(required=True)
    corrected_qty = fields.Float(string="Corrected Quantity")
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium", required=True, tracking=True)
    checked_on = fields.Date(
        string="Checked On", required=True, default=fields.Date.context_today,
        tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("corrected", "Corrected"),
         ("dismissed", "Dismissed")],
        default="open", required=True, copy=False, tracking=True, index=True)
    is_suspicious = fields.Boolean(
        string="Suspicious", compute="_compute_is_suspicious", store=True,
        index=True)
    correction_note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("state")
    def _compute_is_suspicious(self):
        for check in self:
            check.is_suspicious = check.state == "open"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "unit.check") or _("New")
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for check in self:
            if check.quantity <= 0:
                raise ValidationError(_(
                    "The quantity must be greater than zero."))

    @api.constrains("corrected_qty", "state")
    def _check_corrected_qty(self):
        for check in self:
            if check.state == "corrected" and check.corrected_qty <= 0:
                raise ValidationError(_(
                    "A corrected check must have a corrected quantity "
                    "greater than zero."))

    @api.constrains("expected_unit", "entered_unit")
    def _check_units(self):
        for check in self:
            if (check.expected_unit or "").strip().lower() == (
                    check.entered_unit or "").strip().lower():
                raise ValidationError(_(
                    "Expected and entered units must differ for a "
                    "suspicious check."))

    def action_correct(self):
        for check in self:
            if check.state != "open":
                raise UserError(_("Only an open check can be corrected."))
            if check.corrected_qty <= 0:
                raise UserError(_(
                    "Set a corrected quantity greater than zero before "
                    "correcting."))
            check.state = "corrected"
            check.message_post(body=_(
                "Check corrected: quantity set to %s %s.",
                check.corrected_qty, check.expected_unit))
        return True

    def action_dismiss(self):
        for check in self:
            if check.state != "open":
                raise UserError(_("Only an open check can be dismissed."))
            check.state = "dismissed"
            check.message_post(body=_("The check was dismissed."))
        return True

    def action_reopen(self):
        for check in self:
            if check.state == "open":
                raise UserError(_("The check is already open."))
            check.state = "open"
        return True
