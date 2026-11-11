# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class QuarantineCase(models.Model):
    _name = "quarantine.case"
    _description = "Quarantine Case"
    _inherit = ["mail.thread"]
    _order = "quarantined_on desc, id desc"

    name = fields.Char(
        required=True, copy=False, default="New", tracking=True,
        help="Reference of the quarantine case.")
    product_name = fields.Char(
        string="Product", required=True, tracking=True,
        help="Product held in quarantine.")
    lot_name = fields.Char(
        string="Lot / Serial", tracking=True,
        help="Lot or serial identifier, when available.")
    quantity = fields.Float(
        required=True, default=1.0, tracking=True,
        help="Quantity held in quarantine.")
    location_name = fields.Char(
        string="Location", required=True, tracking=True,
        help="Location where the stock is held.")
    reason = fields.Selection(
        [("damage", "Damage"), ("label_issue", "Label Issue"),
         ("temperature", "Temperature Doubt"), ("quality", "Quality Doubt"),
         ("other", "Other")],
        default="other", required=True, tracking=True,
        help="Reason the stock was quarantined.")
    quarantined_on = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True,
        help="Date the stock was moved to quarantine.")
    state = fields.Selection(
        [("quarantine", "In Quarantine"), ("released", "Released"),
         ("returned", "Returned"), ("scrapped", "Scrapped")],
        default="quarantine", required=True, tracking=True, index=True)
    decision_date = fields.Date(
        string="Decision Date", readonly=True, copy=False,
        help="Date the decision was recorded.")
    decision_note = fields.Text(
        help="Explanation of the decision taken.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "quarantine.case") or _("QD-%s") % fields.Date.context_today(self)
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s must be greater than zero.", record.name))

    @api.constrains("quarantined_on", "decision_date")
    def _check_dates(self):
        for record in self:
            if record.decision_date and record.decision_date < record.quarantined_on:
                raise ValidationError(_(
                    "The decision date of %s cannot be before the quarantine date.",
                    record.name))

    def _set_decision(self, state, note=None):
        for record in self:
            if record.state != "quarantine":
                raise UserError(_("Only quarantined cases can be decided."))
            values = {
                "state": state,
                "decision_date": fields.Date.context_today(record),
            }
            if note:
                values["decision_note"] = note
            record.write(values)
        return True

    def action_release(self):
        self._set_decision("released")
        for record in self:
            record.message_post(body=_("Case released back to stock."))
        return True

    def action_return(self):
        self._set_decision("returned")
        for record in self:
            record.message_post(body=_("Case marked for return to supplier."))
        return True

    def action_scrap(self):
        self._set_decision("scrapped")
        for record in self:
            record.message_post(body=_("Case marked as scrapped."))
        return True

    def action_reopen(self):
        for record in self:
            if record.state == "quarantine":
                raise UserError(_("Quarantined cases cannot be reopened."))
            record.write({"state": "quarantine", "decision_date": False})
            record.message_post(body=_("Case reopened and moved back to quarantine."))
        return True
