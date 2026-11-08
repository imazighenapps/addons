# -*- coding: utf-8 -*-
from odoo import models, _

from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        # Only a manual change of an already posted number is suspicious: the
        # posting itself writes the name while the entry is still a draft.
        if "name" in vals and "state" not in vals:
            for move in self:
                if move.state != "posted" or not move.name:
                    continue
                if move.name == vals["name"]:
                    continue
                rule = self.env["gapless.rule"].search([
                    ("company_id", "=", move.company_id.id),
                    ("active", "=", True),
                    "|",
                    ("journal_id", "=", False),
                    ("journal_id", "=", move.journal_id.id),
                ], limit=1, order="journal_id")
                if not rule:
                    continue
                if rule.mode == "block":
                    raise UserError(_(
                        "The number of a posted entry cannot be changed by "
                        "hand. Ask an accountant to reverse the entry instead."))
                self.env["gapless.issue"].create({
                    "rule_id": rule.id,
                    "company_id": move.company_id.id,
                    "journal_id": move.journal_id.id,
                    "kind": "manual",
                    "move_id": move.id,
                    "move_name": move.name,
                    "expected": move.name,
                    "found": vals["name"],
                    "issue_date": move.date,
                })
        return super().write(vals)
