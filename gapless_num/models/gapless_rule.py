# -*- coding: utf-8 -*-
import re
from datetime import timedelta

from odoo import api, fields, models, _


class GaplessRule(models.Model):
    _name = "gapless.rule"
    _description = "Numbering Rule"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    journal_id = fields.Many2one(
        "account.journal", string="Journal",
        help="Leave empty to apply the rule to every journal of the company.")
    mode = fields.Selection(
        [("warn", "Warn only"), ("block", "Block manual renumbering")],
        default="warn", required=True,
        help="Warn creates an anomaly when a posted number is changed by "
             "hand. Block refuses the change.")
    tolerance = fields.Integer(
        default=0,
        help="Number of missing numbers tolerated in a row before an "
             "anomaly is reported.")
    active = fields.Boolean(default=True)
    note = fields.Text()

    _sql_constraints = [
        ('company_journal_uniq', "unique(company_id, journal_id)", "A numbering rule already exists for this company and journal."),
    ]

    def action_scan(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        scan = self.env["gapless.scan"].create({
            "date_from": today - timedelta(days=365),
            "date_to": today,
            "rule_id": self.id,
            "company_id": self.company_id.id,
        })
        return scan.action_run()

    @staticmethod
    def split_number(name):
        """Return (prefix, number, width) from a legal number, or False.

        "INV/2026/00012" gives ("INV/2026/", 12, 5). A name without a
        trailing numeric part is not a legal sequence and is ignored.
        """
        if not name:
            return False
        match = re.match(r"^(.*?)(\d+)\s*$", name)
        if not match:
            return False
        return match.group(1), int(match.group(2)), len(match.group(2))
