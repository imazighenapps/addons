# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PatrolStop(models.Model):
    _name = "patrol.stop"
    _description = "Patrol Stop"
    _inherit = ["mail.thread"]
    _order = "checked_at, id"

    name = fields.Char(
        string="Checkpoint", required=True, tracking=True,
        help="Name of the checkpoint visited during the round.")
    round_id = fields.Many2one(
        "patrol.round", string="Round", required=True,
        ondelete="cascade", index=True, tracking=True)
    status = fields.Selection(
        [("visited", "Visited"), ("skipped", "Skipped")],
        default="visited", required=True, tracking=True, index=True)
    checked_at = fields.Datetime(
        string="Checked At", default=fields.Datetime.now, tracking=True,
        help="Time the checkpoint was checked or marked.")
    finding = fields.Boolean(
        default=False, tracking=True,
        help="Ticked when an issue was observed at this checkpoint.")
    observation = fields.Text(
        help="What was seen at the checkpoint during the visit.")
    company_id = fields.Many2one(
        related="round_id.company_id", store=True, readonly=True, index=True)

    @api.constrains("checked_at", "round_id")
    def _check_checked_at(self):
        for stop in self:
            if stop.round_id and stop.checked_at \
                    and stop.round_id.start_at \
                    and stop.checked_at < stop.round_id.start_at:
                raise ValidationError(_(
                    "The check time of %s cannot come before the start of "
                    "round %s.", stop.name, stop.round_id.name))

    @api.constrains("status", "finding")
    def _check_skipped_finding(self):
        for stop in self:
            if stop.status == "skipped" and stop.finding:
                raise ValidationError(_(
                    "A skipped checkpoint cannot be reported with a finding."))
