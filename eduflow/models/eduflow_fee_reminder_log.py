# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowFeeReminderLog(models.Model):
    """F1.3 -- journal of automatic reminders sent for a fee, one line per
    milestone (e.g. J-7/J0/J+7) so the cron never sends the same milestone
    twice (idempotency required by the technical specification)."""
    _name = 'eduflow.fee.reminder.log'
    _description = "School Fee Reminder Log"
    _order = 'date desc'

    fee_id = fields.Many2one('eduflow.fee', string="Fee / Due", required=True, ondelete='cascade')
    milestone = fields.Integer(
        string="Milestone (days)",
        help="Offset in days relative to the due date (negative = before, 0 = due date, "
             "positive = after).")
    date = fields.Date(string="Sent On", required=True, default=fields.Date.context_today)
