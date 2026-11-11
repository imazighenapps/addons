# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PatrolRound(models.Model):
    _name = "patrol.round"
    _description = "Patrol Round"
    _inherit = ["mail.thread"]
    _order = "start_at desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Round %s")
        % fields.Date.context_today(self), tracking=True,
        help="Reference of the patrol round.")
    guard_name = fields.Char(
        string="Guard", required=True, tracking=True,
        help="Name of the guard who performed the round.")
    route = fields.Char(
        required=True, tracking=True,
        help="Route or area covered during the round.")
    start_at = fields.Datetime(
        string="Started At", required=True,
        default=fields.Datetime.now, tracking=True)
    end_at = fields.Datetime(string="Ended At", tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Completed")],
        default="draft", required=True, tracking=True, index=True)
    stop_ids = fields.One2many(
        "patrol.stop", "round_id", string="Stops")
    stop_count = fields.Integer(
        string="Stops", compute="_compute_counts", store=True)
    skipped_count = fields.Integer(
        string="Skipped", compute="_compute_counts", store=True)
    finding_count = fields.Integer(
        string="Findings", compute="_compute_counts", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("stop_ids", "stop_ids.status", "stop_ids.finding")
    def _compute_counts(self):
        for round_rec in self:
            stops = round_rec.stop_ids
            round_rec.stop_count = len(stops)
            round_rec.skipped_count = len(
                stops.filtered(lambda stop: stop.status == "skipped"))
            round_rec.finding_count = len(
                stops.filtered(lambda stop: stop.finding))

    @api.constrains("start_at", "end_at")
    def _check_dates(self):
        for round_rec in self:
            if round_rec.end_at and round_rec.end_at < round_rec.start_at:
                raise ValidationError(_(
                    "The end time of %s cannot come before its start time.",
                    round_rec.name))

    def action_done(self):
        for round_rec in self:
            if round_rec.state != "draft":
                raise ValidationError(_(
                    "The patrol round %s is already completed.",
                    round_rec.name))
            round_rec.write({
                "state": "done",
                "end_at": round_rec.end_at or fields.Datetime.now(),
            })
            round_rec.message_post(body=_(
                "The patrol round has been completed."))
        return True
