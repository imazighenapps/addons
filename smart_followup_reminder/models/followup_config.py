# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class FollowupConfig(models.Model):
    _name = 'followup.config'
    _description = 'Follow-up Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True)
    team_id = fields.Many2one(
        'crm.team', string='Sales Team', required=True, ondelete='cascade'
    )
    delay_1 = fields.Integer(
        string='Days Before 1st Reminder', default=3,
        help='Number of days without reply before sending the first reminder.'
    )
    delay_2 = fields.Integer(
        string='Days Before 2nd Reminder', default=5,
        help='Number of days without reply before sending the second reminder.'
    )
    delay_3 = fields.Integer(
        string='Days Before Manager Escalation', default=7,
        help='Number of days without reply before escalating to the manager.'
    )
    min_amount = fields.Float(
        string='Minimum Amount', default=0.0,
        help='Minimum order amount to trigger follow-up reminders.'
    )
    template_id = fields.Many2one(
        'mail.template', string='Email Template',
        domain=[('model', '=', 'sale.order')]
    )
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_team', 'UNIQUE(team_id)', _('A configuration already exists for this sales team.'))
    ]
