# -*- coding: utf-8 -*-
from odoo import fields, models, _


class IdeaReview(models.Model):
    _name = "idea.review"
    _description = "Idea Review"
    _inherit = ["mail.thread"]
    _order = "reviewed_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Review %s")
        % fields.Date.context_today(self),
        help="Reference of the review, generated at creation.")
    proposal_id = fields.Many2one(
        "idea.proposal", string="Idea", required=True,
        ondelete="cascade", index=True, tracking=True)
    reviewer_id = fields.Many2one(
        "res.partner", string="Reviewer", required=True, tracking=True)
    decision = fields.Selection(
        [("accept", "Accept"), ("reject", "Reject"), ("note", "Note")],
        default="note", required=True, tracking=True)
    reviewed_on = fields.Date(
        string="Reviewed On", required=True,
        default=fields.Date.context_today, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    comment = fields.Text(
        help="Decision note explaining why the idea was accepted or rejected.")
