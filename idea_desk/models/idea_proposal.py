# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IdeaProposal(models.Model):
    _name = "idea.proposal"
    _description = "Improvement Idea"
    _inherit = ["mail.thread"]
    _order = "submitted_on desc, id desc"

    name = fields.Char(required=True, tracking=True)
    author_id = fields.Many2one(
        "res.partner", string="Author", required=True, tracking=True,
        help="Person who submitted the improvement idea.")
    area = fields.Char(
        help="Area or process the idea aims to improve.")
    expected_gain = fields.Float(
        string="Expected Gain", default=0.0,
        help="Estimated gain of the idea, in the unit used by the team.")
    submitted_on = fields.Date(
        string="Submitted On", required=True,
        default=fields.Date.context_today, tracking=True)
    evaluated_on = fields.Date(
        string="Evaluated On", readonly=True, copy=False)
    implemented_on = fields.Date(
        string="Implemented On", readonly=True, copy=False)
    review_ids = fields.One2many(
        "idea.review", "proposal_id", string="Reviews")
    review_count = fields.Integer(
        string="Reviews", compute="_compute_reviews")
    state = fields.Selection(
        [("submitted", "Submitted"), ("accepted", "Accepted"),
         ("rejected", "Rejected"), ("implemented", "Implemented")],
        default="submitted", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("review_ids")
    def _compute_reviews(self):
        for idea in self:
            idea.review_count = len(idea.review_ids)

    @api.constrains("expected_gain")
    def _check_expected_gain(self):
        for idea in self:
            if idea.expected_gain < 0:
                raise ValidationError(_(
                    "The expected gain of %s cannot be negative.", idea.name))

    def action_accept(self):
        for idea in self:
            if idea.state != "submitted":
                raise ValidationError(_(
                    "Only a submitted idea can be accepted: %s.", idea.name))
            idea.write({
                "state": "accepted",
                "evaluated_on": fields.Date.context_today(idea),
            })
            idea.message_post(body=_("The idea was accepted for implementation."))
        return True

    def action_reject(self):
        for idea in self:
            if idea.state != "submitted":
                raise ValidationError(_(
                    "Only a submitted idea can be rejected: %s.", idea.name))
            idea.write({
                "state": "rejected",
                "evaluated_on": fields.Date.context_today(idea),
            })
            idea.message_post(body=_("The idea was rejected after review."))
        return True

    def action_implement(self):
        for idea in self:
            if idea.state != "accepted":
                raise ValidationError(_(
                    "Only an accepted idea can be marked implemented: %s.",
                    idea.name))
            idea.write({
                "state": "implemented",
                "implemented_on": fields.Date.context_today(idea),
            })
            idea.message_post(body=_("The idea was implemented and credited."))
        return True
