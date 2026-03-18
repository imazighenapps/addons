# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class WaitingRoom(models.Model):
    _name = 'waiting.room'
    _description = 'Waiting Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Room Name', required=True, tracking=True)
    code = fields.Char(string='Room Code', size=20, required=True)
    active = fields.Boolean(default=True)
    location = fields.Char(string='Location / Floor')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company, required=True)
    department_ids = fields.Many2many(
        'waiting.room.department',
        string='Departments / Services')
    display_token = fields.Char(
        string='Display Token',
        help='Unique token for public TV display URL',
        copy=False)
    display_url = fields.Char(
        string='Display URL', compute='_compute_display_url', store=False)
    kiosk_url = fields.Char(
        string='Kiosk URL', compute='_compute_display_url', store=False)
    is_open = fields.Boolean(string='Open', default=True, tracking=True)
    capacity = fields.Integer(string='Room Capacity', default=20)
    notes = fields.Text(string='Notes')
    color = fields.Integer(string='Color')
    background_image = fields.Binary(string='Display Background Image')
    logo = fields.Binary(string='Display Logo')
    welcome_message = fields.Char(
        string='Welcome Message',
        default='Welcome! Please take a seat.',
        translate=True)
    footer_message = fields.Char(
        string='Footer Message',
        default='Thank you for your patience.',
        translate=True)
    ticker_messages = fields.Text(
        string='Ticker Messages',
        default='Thank you for your patience. | Please remain seated until your token is called. | Watch the screen for your token number.',
        help='Messages separated by | shown in the scrolling ticker at the bottom of the display screen.',
        translate=True)
    show_estimated_time = fields.Boolean(
        string='Show Estimated Wait Time', default=True)
    show_visitor_name = fields.Boolean(
        string='Show Visitor Name on Display',
        default=True,
        help='When disabled, only the token number is shown on the TV display '
             'and the call overlay. The visitor\'s name is never visible to '
             'other patients. Recommended for medical, legal, or privacy-sensitive contexts.')
    show_weather = fields.Boolean(
        string='Show Date/Time on Display', default=True)
    audio_enabled = fields.Boolean(
        string='Audio Announcements', default=True)
   
    line_ids = fields.One2many(
        'waiting.room.line', 'room_id', string='Queue')
    line_count = fields.Integer(
        string='Total in Queue', compute='_compute_stats')
    waiting_count = fields.Integer(
        string='Waiting', compute='_compute_stats')
    in_service_count = fields.Integer(
        string='In Service', compute='_compute_stats')
    done_today_count = fields.Integer(
        string='Done Today', compute='_compute_stats')
    avg_wait_time = fields.Float(
        string='Avg Wait (min)', compute='_compute_stats')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('display_token'):
                vals['display_token'] = self.env['ir.sequence'].next_by_code(
                    'waiting.room.display.token') or \
                    self._generate_token()
        return super().create(vals_list)

    def _generate_token(self):
        import uuid
        return uuid.uuid4().hex[:12].upper()

    def _compute_display_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        for rec in self:
            if rec.display_token:
                rec.display_url = f"{base_url}/waiting-room/display/{rec.display_token}"
                rec.kiosk_url = f"{base_url}/waiting-room/kiosk/{rec.display_token}"
            else:
                rec.display_url = ''
                rec.kiosk_url = ''

    @api.depends('line_ids', 'line_ids.state')
    def _compute_stats(self):
        today = fields.Date.today()
        for rec in self:
            lines = rec.line_ids
            waiting = lines.filtered(lambda l: l.state == 'waiting')
            in_service = lines.filtered(lambda l: l.state == 'in_service')
            done_today = lines.filtered(
                lambda l: l.state == 'done' and
                l.done_time and l.done_time.date() == today)
            rec.line_count = len(lines.filtered(
                lambda l: l.state in ['waiting', 'called', 'in_service']))
            rec.waiting_count = len(waiting)
            rec.in_service_count = len(in_service)
            rec.done_today_count = len(done_today)
            # compute avg wait
            wait_times = []
            for line in done_today:
                if line.call_time and line.check_in_time:
                    delta = (line.call_time - line.check_in_time).total_seconds() / 60
                    wait_times.append(delta)
            rec.avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0.0

    def action_open_display(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.display_url,
            'target': 'new',
        }

    def action_open_kiosk(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.kiosk_url,
            'target': 'new',
        }

    def action_view_queue(self):
        self.ensure_one()
        return {
            'name': _('Queue — %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'waiting.room.line',
            'view_mode': 'list,form,kanban',
            'domain': [('room_id', '=', self.id),
                       ('state', 'in', ['waiting', 'called', 'in_service'])],
            'context': {'default_room_id': self.id},
        }

    def action_toggle_open(self):
        for rec in self:
            rec.is_open = not rec.is_open
