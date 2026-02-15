# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class MeetingManagement(models.Model):
    _name = 'meeting.management'
    _description = 'Meeting Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(
        string='Meeting Title',
        required=True,
        tracking=True
    )
    date_start = fields.Datetime(
        string='Start Date',
        required=True,
        tracking=True
    )
    date_end = fields.Datetime(
        string='End Date',
        required=True,
        tracking=True
    )
    duration_planned = fields.Float(
        string='Planned Duration (hours)',
        compute='_compute_duration_planned',
        store=True,
        digits=(12, 2)
    )
    duration_actual = fields.Float(
        string='Actual Duration (hours)',
        compute='_compute_duration_actual',
        store=True,
        digits=(12, 2)
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        tracking=True
    )
    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        domain=[('is_company', '=', True)],
        tracking=True
    )
    participant_ids = fields.One2many(
        'meeting.participant',
        'meeting_id',
        string='Participants'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('validated', 'Validated'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    active = fields.Boolean(default=True)
    
    participant_count = fields.Integer(
        string='Participants',
        compute='_compute_participant_count'
    )
    
    notes = fields.Text(string='Notes')
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.uid
    )

    role  = fields.Char()
    
    @api.depends('date_start', 'date_end')
    def _compute_duration_planned(self):
        for meeting in self:
            if meeting.date_start and meeting.date_end:
                delta = meeting.date_end - meeting.date_start
                meeting.duration_planned = delta.total_seconds() / 3600.0
            else:
                meeting.duration_planned = 0.0
    
    @api.depends('participant_ids.duration_actual')
    def _compute_duration_actual(self):
        for meeting in self:
            meeting.duration_actual = sum(meeting.participant_ids.mapped('duration_actual'))
    
    @api.depends('participant_ids')
    def _compute_participant_count(self):
        for meeting in self:
            meeting.participant_count = len(meeting.participant_ids)
    
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for meeting in self:
            if meeting.date_start and meeting.date_end:
                if meeting.date_end <= meeting.date_start:
                    raise ValidationError(_('End date must be after start date.'))
    
    def action_set_planned(self):
        self.ensure_one()
        if not self.participant_ids:
            raise UserError(_('Cannot plan a meeting without participants.'))
        self.state = 'planned'
    
    def action_set_done(self):
        self.ensure_one()
        self.state = 'done'
    
    def action_validate(self):
        self.ensure_one()
        if not self.env.user.has_group('meeting_management.group_meeting_manager'):
            raise UserError(_('Only managers can validate meetings.'))
        if self.state != 'done':
            raise UserError(_('Only meetings in Done status can be validated.'))
        self.state = 'validated'
    
    def action_view_participants(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Participants'),
            'res_model': 'meeting.participant',
            'view_mode': 'list,form',
            'domain': [('meeting_id', '=', self.id)],
            'context': {'default_meeting_id': self.id},
            'target': 'current',
        }
    
    def action_view_project(self):
        self.ensure_one()
        if not self.project_id:
            raise UserError(_('No project linked to this meeting.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project'),
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': self.project_id.id,
            'target': 'current',
        }
    
    @api.model
    def _cron_update_meeting_status(self):
        now = fields.Datetime.now()
        meetings = self.search([
            ('state', '=', 'planned'),
            ('date_end', '<', now)
        ])
        if meetings:
            meetings.write({'state': 'done'})
        return True
