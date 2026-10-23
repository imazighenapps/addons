# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Nis2Control(models.Model):
    _name = "nis2.control"
    _description = "NIS2 Article 21 Control"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True, translate=True)
    code = fields.Char(required=True, help="Article 21 letter (a) to (j).")
    recyf_ref = fields.Char(string="ReCyF Reference")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    owner_id = fields.Many2one("res.users", string="Owner", tracking=True)
    maturity = fields.Selection(
        [
            ("none", "Not Implemented"),
            ("partial", "Partially Implemented"),
            ("done", "Implemented"),
            ("planned", "Planned"),
        ],
        default="none",
        required=True,
        tracking=True,
    )
    review_frequency = fields.Selection(
        [("quarterly", "Quarterly"), ("biannual", "Biannual"), ("yearly", "Yearly")],
        default="yearly",
    )
    next_review = fields.Date(string="Next Review")
    description = fields.Text(translate=True)
    evidence_ids = fields.Many2many("nis2.evidence", string="Evidence")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_company_unique", "UNIQUE(code, company_id)", "Control code must be unique per company."),
    ]

    def action_schedule_review(self):
        from datetime import date
        from dateutil.relativedelta import relativedelta
        for rec in self:
            months = {"quarterly": 3, "biannual": 6, "yearly": 12}[rec.review_frequency]
            rec.next_review = date.today() + relativedelta(months=months)
            rec.message_post(body=_("Next review scheduled on %s.") % rec.next_review)
