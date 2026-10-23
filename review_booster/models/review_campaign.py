# -*- coding: utf-8 -*-
from odoo import fields, models


class ReviewCampaign(models.Model):
    _name = "review.campaign"
    _description = "Review Request Campaign"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    google_url = fields.Char(string="Google Review URL", required=True)
    delay_days = fields.Integer(string="Send After (days)", default=3)
    trigger = fields.Selection(
        [("invoice", "On Invoice Posting"), ("delivery", "On Delivery Done")],
        default="invoice",
        required=True,
    )
    active = fields.Boolean(default=True)
