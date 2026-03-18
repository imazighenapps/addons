# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WaitingRoomDepartment(models.Model):
    _name = 'waiting.room.department'
    _description = 'Waiting Room Department / Service'
    _order = 'sequence, name'

    name = fields.Char(string='Department Name', required=True, translate=True)
    code = fields.Char(string='Code', size=10, required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    color = fields.Integer(string='Color Index', default=0)
    icon = fields.Char(string='Icon (FA)', default='fa-stethoscope',
                       help='FontAwesome icon class, e.g. fa-stethoscope')
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description', translate=True)
    avg_service_duration = fields.Integer(
        string='Avg. Service Duration (min)', default=15,
        help='Used to estimate waiting time')
    waiting_room_ids = fields.Many2many(
        'waiting.room', string='Waiting Rooms')
    queue_count = fields.Integer(
        string='In Queue', compute='_compute_queue_count')
    waiting_count = fields.Integer(
        string='Waiting', compute='_compute_queue_count')
    display_color = fields.Char(
        string='Display Color', default='#6c5ce7',
        help='Hex color for display screen')
    responsible_user_id = fields.Many2one(
        'res.users', string='Responsible')
    auto_call_next = fields.Boolean(
        string='Auto-call Next', default=False,
        help='Automatically call next patient when current is done')

    @api.depends()
    def _compute_queue_count(self):
        for rec in self:
            lines = self.env['waiting.room.line'].search([
                ('department_id', '=', rec.id),
                ('state', 'in', ['waiting', 'called', 'in_service']),
            ])
            rec.queue_count = len(lines)
            rec.waiting_count = len(lines.filtered(
                lambda l: l.state == 'waiting'))

    def get_current_token(self):
        self.ensure_one()
        line = self.env['waiting.room.line'].search([
            ('department_id', '=', self.id),
            ('state', '=', 'in_service'),
        ], limit=1, order='call_time desc')
        return line

    def get_next_waiting(self):
        self.ensure_one()
        line = self.env['waiting.room.line'].search([
            ('department_id', '=', self.id),
            ('state', '=', 'waiting'),
        ], limit=1, order='priority desc, sequence asc, token_number asc')
        return line
