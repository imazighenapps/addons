# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    bradford_included = fields.Boolean(string="Count in Bradford", default=False)
    bradford_code = fields.Selection(
        [("sickness_short", "Short Sickness"), ("sickness_long", "Long Sickness"),
         ("occupational", "Occupational (excluded by default)"),
         ("maternity", "Maternity/Paternity (excluded)"),
         ("other_excluded", "Other (excluded)")],
        string="Bradford Category",
    )


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    bradford_s = fields.Integer(string="Spells (52w)", compute="_compute_bradford",
                                store=True)
    bradford_d = fields.Float(string="Days (52w)", compute="_compute_bradford",
                              store=True)
    bradford_score = fields.Integer(compute="_compute_bradford", store=True)
    bradford_band = fields.Char(compute="_compute_bradford", store=True)
    bradford_date = fields.Date(compute="_compute_bradford", store=True)

    def _compute_bradford(self):
        for emp in self:
            spells = self.env["bradford.spell"].search(
                [("employee_id", "=", emp.id)])
            s = len(spells)
            d = sum(spells.mapped("days"))
            score = s * s * int(round(d))
            emp.bradford_s = s
            emp.bradford_d = d
            emp.bradford_score = score
            emp.bradford_band = self.env["bradford.threshold"]._band_for(score)
            emp.bradford_date = fields.Date.today()

    def action_bradford_recompute(self):
        for emp in self:
            emp._bradford_rebuild_spells()
            emp._compute_bradford()
        return True

    def _bradford_rebuild_spells(self):
        self.ensure_one()
        window_start = fields.Date.today() - timedelta(days=364)
        leaves = self.env["hr.leave"].search([
            ("employee_id", "=", self.id),
            ("state", "in", ("validate", "validate1")),
            ("holiday_status_id.bradford_included", "=", True),
            ("date_from", ">=", window_start),
        ], order="date_from")
        self.env["bradford.spell"].search(
            [("employee_id", "=", self.id)]).unlink()
        spells, current = [], None
        for leave in leaves:
            start = leave.date_from.date() if hasattr(leave.date_from, "date") else leave.date_from
            end = leave.date_to.date() if hasattr(leave.date_to, "date") else leave.date_to
            days = leave.number_of_days or 0.0
            if current and start <= current["end"] + timedelta(days=2):
                current["end"] = max(current["end"], end)
                current["days"] += days
                current["leaves"].append(leave.id)
            else:
                if current:
                    spells.append(current)
                current = {"start": start, "end": end, "days": days,
                           "leaves": [leave.id]}
        if current:
            spells.append(current)
        for sp in spells:
            self.env["bradford.spell"].create({
                "employee_id": self.id,
                "date_from": sp["start"], "date_to": sp["end"],
                "days": sp["days"], "leave_ids": [(6, 0, sp["leaves"])],
            })


class BradfordSpell(models.Model):
    _name = "bradford.spell"
    _description = "Bradford Absence Spell (read-only)"
    _order = "date_from desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    company_id = fields.Many2one("res.company", related="employee_id.company_id",
                                 store=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    days = fields.Float()
    leave_ids = fields.Many2many("hr.leave", string="Leaves")
    excluded_reason = fields.Char()


class BradfordHistory(models.Model):
    _name = "bradford.score.history"
    _description = "Bradford Score History"
    _order = "date desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    date = fields.Date(default=fields.Date.today)
    s_spells = fields.Integer(string="S")
    d_days = fields.Float(string="D")
    score = fields.Integer(string="B")
    band = fields.Char()


class BradfordThreshold(models.Model):
    _name = "bradford.threshold"
    _description = "Bradford Threshold Band"
    _order = "min_score"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    min_score = fields.Integer(string="From Score", required=True)
    action = fields.Char(string="Action (supportive wording)")
    role_notified = fields.Selection(
        [("manager", "Manager"), ("hr", "HR"), ("both", "Manager + HR")],
        default="manager",
    )

    @api.model
    def _band_for(self, score):
        band = self.search([("min_score", "<=", score)], order="min_score desc",
                           limit=1)
        return band.name if band else ""

    @api.model
    def _cron_recompute_all(self):
        for emp in self.env["hr.employee"].search([("active", "=", True)]):
            emp._bradford_rebuild_spells()
            emp._compute_bradford()
            hist = {
                "employee_id": emp.id, "date": fields.Date.today(),
                "s_spells": emp.bradford_s, "d_days": emp.bradford_d,
                "score": emp.bradford_score, "band": emp.bradford_band,
            }
            self.env["bradford.score.history"].create(hist)
            for th in self.search([("min_score", "<=", emp.bradford_score)]):
                open_alert = self.env["bradford.alert"].search_count([
                    ("employee_id", "=", emp.id), ("threshold_id", "=", th.id),
                    ("state", "=", "open")])
                if not open_alert and emp.bradford_score >= th.min_score and th.min_score > 0:
                    self.env["bradford.alert"].create({
                        "employee_id": emp.id, "threshold_id": th.id,
                        "score_snapshot": emp.bradford_score,
                    })
        old = fields.Date.today() - timedelta(days=730)
        self.env["bradford.score.history"].search([("date", "<", old)]).unlink()
        return True


class BradfordAlert(models.Model):
    _name = "bradford.alert"
    _description = "Bradford Threshold Alert"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    threshold_id = fields.Many2one("bradford.threshold", required=True)
    score_snapshot = fields.Integer()
    state = fields.Selection(
        [("open", "Open"), ("acknowledged", "Acknowledged"), ("closed", "Closed")],
        default="open",
        tracking=True,
    )
    due_date = fields.Date()

    def action_ack(self):
        self.write({"state": "acknowledged"})

    def action_close(self):
        self.write({"state": "closed"})


class RtwInterview(models.Model):
    _name = "hr.rtw.interview"
    _description = "Return-to-Work Interview (no diagnosis stored)"
    _inherit = ["mail.thread"]
    _order = "date_return desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    company_id = fields.Many2one("res.company", related="employee_id.company_id",
                                 store=True)
    spell_id = fields.Many2one("bradford.spell", string="Absence Spell")
    leave_id = fields.Many2one("hr.leave", string="Leave")
    date_return = fields.Date(default=fields.Date.today, required=True)
    interviewer_id = fields.Many2one("res.users", string="Interviewer",
                                     default=lambda self: self.env.user)
    fitness_confirmed = fields.Boolean(string="Fit to Return Confirmed")
    declared_reason = fields.Char(
        string="Declared Motive (no diagnosis)",
        help="Short administrative motive only. Never store medical details.")
    adjustments = fields.Text(string="Agreed Adjustments")
    next_step = fields.Char()
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Done"), ("waived", "Waived")],
        default="todo",
        tracking=True,
    )

    def action_done(self):
        self.write({"state": "done"})

    def action_waive(self):
        self.write({"state": "waived"})
