# -*- coding: utf-8 -*-
from odoo import fields, models, _


class GaplessScan(models.TransientModel):
    _name = "gapless.scan"
    _description = "Numbering Scan"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    journal_ids = fields.Many2many("account.journal", string="Journals")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    rule_id = fields.Many2one("gapless.rule", string="Rule")

    def _rule_for(self, move):
        if self.rule_id:
            return self.rule_id
        rules = self.env["gapless.rule"].search([
            ("company_id", "=", move.company_id.id),
            ("active", "=", True),
        ])
        specific = rules.filtered(lambda r: r.journal_id == move.journal_id)
        if specific:
            return specific[:1]
        return rules.filtered(lambda r: not r.journal_id)[:1]

    def _create_issue(self, rule, move, kind, expected="", found=""):
        Issue = self.env["gapless.issue"]
        domain = [
            ("company_id", "=", move.company_id.id),
            ("journal_id", "=", move.journal_id.id),
            ("kind", "=", kind),
            ("expected", "=", expected),
            ("found", "=", found),
        ]
        existing = Issue.search(domain, limit=1)
        if existing:
            return existing
        return Issue.create({
            "rule_id": rule.id if rule else False,
            "company_id": move.company_id.id,
            "journal_id": move.journal_id.id,
            "kind": kind,
            "move_id": move.id,
            "move_name": move.name,
            "expected": expected,
            "found": found,
            "issue_date": move.date or fields.Date.context_today(self),
        })

    def action_run(self):
        self.ensure_one()
        domain = [
            ("state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
        ]
        journals = self.journal_ids
        if not journals and self.rule_id.journal_id:
            journals = self.rule_id.journal_id
        if journals:
            domain.append(("journal_id", "in", journals.ids))
        moves = self.env["account.move"].search(domain, order="journal_id, name")
        groups = {}
        for move in moves:
            split = self.env["gapless.rule"].split_number(move.name)
            if not split:
                continue
            prefix, number, width = split
            key = (move.journal_id.id, prefix)
            groups.setdefault(key, {"width": width, "rows": []})
            groups[key]["width"] = max(groups[key]["width"], width)
            groups[key]["rows"].append((number, move.name, move))

        issues = self.env["gapless.issue"]
        for (_journal_id, prefix), group in groups.items():
            width = group["width"]
            rows = sorted(group["rows"], key=lambda row: (row[0], row[2].date))
            rule = self._rule_for(rows[0][2])
            tolerance = rule.tolerance if rule else 0
            seen = {}
            previous = None
            for number, name, move in rows:
                if number in seen:
                    issues |= self._create_issue(
                        rule, move, "duplicate", name, name)
                else:
                    seen[number] = move
                if previous is not None:
                    gap = number - previous[0] - 1
                    if gap > tolerance:
                        missing = prefix + str(previous[0] + 1).zfill(width)
                        issues |= self._create_issue(
                            rule, move, "gap", missing, "")
                    if move.date and previous[1].date \
                            and move.date < previous[1].date:
                        issues |= self._create_issue(
                            rule, move, "out_of_order", "", name)
                previous = (number, move)

        action = {
            "type": "ir.actions.act_window",
            "name": _("Numbering Anomalies"),
            "res_model": "gapless.issue",
            "view_mode": "list,form",
        }
        if issues:
            action["domain"] = [("id", "in", issues.ids)]
        else:
            action["domain"] = [
                ("company_id", "=", self.company_id.id),
                ("state", "=", "open"),
            ]
        return action
