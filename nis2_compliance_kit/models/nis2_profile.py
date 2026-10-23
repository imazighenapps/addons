# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Nis2Profile(models.Model):
    _name = "nis2.profile"
    _description = "NIS2 Entity Applicability Profile"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    sector_ids = fields.Many2many("nis2.sector", string="Sectors")
    employees = fields.Integer(string="Employees")
    turnover = fields.Float(string="Turnover (M€)")
    balance_sheet = fields.Float(string="Balance Sheet (M€)")
    candidacy = fields.Selection(
        [
            ("out", "Out of Scope"),
            ("important", "Important Entity (candidate)"),
            ("essential", "Essential Entity (candidate)"),
            ("tbc", "To Be Confirmed"),
        ],
        default="tbc",
        required=True,
        tracking=True,
    )
    review_state = fields.Selection(
        [("draft", "Draft"), ("reviewed", "Reviewed"), ("validated", "Validated")],
        default="draft",
        tracking=True,
    )
    note = fields.Text()

    @api.depends("employees", "turnover", "balance_sheet")
    def _compute_size_hint(self):
        for rec in self:
            big = rec.employees >= 250 or rec.turnover > 50 or rec.balance_sheet > 43
            mid = rec.employees >= 50 or rec.turnover > 10 or rec.balance_sheet > 10
            rec.size_hint = "large" if big else ("medium" if mid else "small")

    size_hint = fields.Selection(
        [("small", "Small"), ("medium", "Medium"), ("large", "Large")],
        compute="_compute_size_hint",
        string="Size Hint",
    )

    def action_suggest_candidacy(self):
        for rec in self:
            annex_i = any(s.annex == "I" for s in rec.sector_ids)
            if rec.size_hint == "large" and annex_i:
                rec.candidacy = "essential"
            elif rec.size_hint in ("medium", "large") and rec.sector_ids:
                rec.candidacy = "important"
            elif not rec.sector_ids or rec.size_hint == "small":
                rec.candidacy = "out"
            else:
                rec.candidacy = "tbc"
            rec.message_post(body=_("Candidacy suggestion computed: %s.") % rec.candidacy)
