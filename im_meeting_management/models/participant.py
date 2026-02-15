# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MeetingParticipant(models.Model):
    _name = 'meeting.participant'
    _description = 'Meeting Participant'
    _rec_name = 'user_id'

    meeting_id = fields.Many2one(
        'meeting.management',
        string='Meeting',
        required=True,
        ondelete='cascade',
        index=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        index=True
    )
    role = fields.Selection([
        ('organizer', 'Organizer'),
        ('participant', 'Participant'),
    ], string='Role', default='participant', required=True)
    
    duration_actual = fields.Float(
        string='Actual Duration (hours)',
        digits=(12, 2),
        default=0.0
    )
    notes = fields.Text(string='Notes')
    
    meeting_name = fields.Char(
        related='meeting_id.name',
        string='Meeting',
        store=True
    )
    meeting_date = fields.Datetime(
        related='meeting_id.date_start',
        string='Meeting Date',
        store=True
    )
    
    _sql_constraints = [
        ('unique_user_meeting', 
         'UNIQUE(meeting_id, user_id)',
         'A user can only be added once per meeting.')
    ]
    
    @api.constrains('duration_actual')
    def _check_duration_actual(self):
        for participant in self:
            if participant.duration_actual < 0:
                raise ValidationError(_('Actual duration cannot be negative.'))
