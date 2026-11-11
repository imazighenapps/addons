# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ForkliftDefect(models.Model):
    _name = "forklift.defect"
    _description = "Forklift Defect"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        string="Defect", required=True, tracking=True,
        help="Short description of the defect found.")
    check_id = fields.Many2one(
        "forklift.check", string="Safety Check", required=True,
        ondelete="cascade", index=True, tracking=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium", required=True, tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("fixed", "Fixed")],
        default="open", required=True, tracking=True, index=True)
    signed_off_on = fields.Date(
        string="Signed Off On", readonly=True, copy=False, tracking=True)
    company_id = fields.Many2one(
        related="check_id.company_id", store=True, readonly=True, index=True)
    detail = fields.Text(help="Additional information about the defect.")

    @api.constrains("state", "signed_off_on")
    def _check_signoff(self):
        for defect in self:
            if defect.state == "fixed" and not defect.signed_off_on:
                raise ValidationError(_(
                    "A fixed defect must have a sign-off date."))

    def action_signoff(self):
        for defect in self:
            if defect.state != "open":
                raise ValidationError(_(
                    "The defect %s is already signed off.", defect.name))
            defect.write({
                "state": "fixed",
                "signed_off_on": fields.Date.context_today(defect),
            })
            defect.message_post(body=_(
                "The defect has been repaired and signed off."))
        return True
