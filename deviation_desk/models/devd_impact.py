# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DevdImpact(models.Model):
    _name = "devd.impact"
    _description = "Deviation Impact Review"
    _inherit = ["mail.thread"]
    _order = "reviewed_on desc, id desc"

    deviation_id = fields.Many2one(
        "devd.deviation", string="Deviation", required=True,
        ondelete="cascade", index=True, tracking=True)
    reviewed_on = fields.Date(
        string="Reviewed On", required=True,
        default=fields.Date.context_today, tracking=True)
    reviewer_id = fields.Many2one(
        "res.users", string="Reviewer", required=True,
        default=lambda self: self.env.user, tracking=True)
    risk_level = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium", required=True, tracking=True)
    judgement = fields.Text(
        string="Judgement", required=True,
        help="Assessment of the impact on product, process or compliance.")
    state = fields.Selection(
        [("open", "Open"), ("done", "Done")],
        default="open", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)

    @api.constrains("reviewed_on")
    def _check_reviewed_on(self):
        for rec in self:
            if rec.reviewed_on and rec.deviation_id.detected_on \
                    and rec.reviewed_on < rec.deviation_id.detected_on:
                raise ValidationError(_(
                    "The impact review for %s cannot predate the deviation.",
                    rec.deviation_id.name))

    def action_done(self):
        for rec in self:
            if rec.state != "open":
                raise ValidationError(_(
                    "Only an open impact review can be completed."))
            rec.state = "done"
        return True
