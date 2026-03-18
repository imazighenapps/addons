# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

PRIORITY_SELECTION = [
    ('0', 'Normal'),
    ('1', 'Priority'),
    ('2', 'Urgent'),
    ('3', 'VIP'),
]

STATE_SELECTION = [
    ('waiting', 'Waiting'),
    ('called', 'Called'),
    ('in_service', 'In Service'),
    ('done', 'Done'),
    ('no_show', 'No Show'),
    ('cancelled', 'Cancelled'),
]

VISITOR_TYPE = [
    ('appointment', 'Appointment'),
    ('walk_in', 'Walk-in'),
    ('urgent', 'Urgent / Emergency'),
    ('vip', 'VIP'),
    ('callback', 'Callback'),
]


class WaitingRoomLine(models.Model):
    _name = 'waiting.room.line'
    _description = 'Waiting Room Queue Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, sequence asc, token_number asc'
    _rec_name = 'display_name'

    # ── Identity ──────────────────────────────────────────────────────────────
    token_number = fields.Integer(
        string='Token #', required=True, readonly=True, default=0)
    token_display = fields.Char(
        string='Token', compute='_compute_token_display', store=True)
    sequence = fields.Integer(string='Sequence', default=10)

    # Optional link to an existing Odoo contact.
    # When set, name/phone are populated automatically via onchange.
    # Kiosk and walk-in visitors leave this empty — name stays a free Char.
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        required=False,
        ondelete='set null',
        tracking=True,
        help='Link to an existing Odoo contact. '
             'Name and phone are filled automatically when selected. '
             'Leave empty for anonymous or walk-in visitors.',
    )

    name = fields.Char(string='Visitor Name', required=True, tracking=True)
    display_name = fields.Char(
        compute='_compute_display_name_field', store=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    notes = fields.Text(string='Notes / Reason')
    visitor_type = fields.Selection(
        VISITOR_TYPE, string='Type', default='walk_in', tracking=True)

    # ── Relations ─────────────────────────────────────────────────────────────
    room_id = fields.Many2one(
        'waiting.room', string='Waiting Room', required=True,
        ondelete='cascade', tracking=True)
    department_id = fields.Many2one(
        'waiting.room.department', string='Department / Service',
        tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Assigned To',
        default=lambda self: self.env.user)
    company_id = fields.Many2one(
        'res.company', related='room_id.company_id', store=True)

    # ── State & Priority ──────────────────────────────────────────────────────
    state = fields.Selection(
        STATE_SELECTION, string='Status',
        default='waiting', required=True, tracking=True,
        group_expand='_expand_states')
    priority = fields.Selection(
        PRIORITY_SELECTION, string='Priority',
        default='0', tracking=True)
    color = fields.Integer(
        string='Color', compute='_compute_color', store=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    check_in_time = fields.Datetime(
        string='Check-in Time', default=fields.Datetime.now, readonly=True)
    call_time = fields.Datetime(string='Called At', readonly=True)
    service_start_time = fields.Datetime(
        string='Service Start', readonly=True)
    done_time = fields.Datetime(string='Done At', readonly=True)

    # ── Computed ──────────────────────────────────────────────────────────────
    wait_duration = fields.Float(
        string='Wait Duration (min)', compute='_compute_durations',
        store=False)
    service_duration = fields.Float(
        string='Service Duration (min)', compute='_compute_durations',
        store=False)
    estimated_wait = fields.Integer(
        string='Est. Wait (min)', compute='_compute_estimated_wait',
        store=False)
    is_late = fields.Boolean(
        string='Overdue', compute='_compute_is_late', store=False)

    # ── Appointment link (optional) ───────────────────────────────────────────
    appointment_id = fields.Many2one(
        'calendar.event', string='Linked Appointment', ondelete='set null')

    # ── Display ───────────────────────────────────────────────────────────────
    call_count = fields.Integer(
        string='Times Called', default=0, readonly=True)
    rating = fields.Selection(
        [('1', '😞'), ('2', '😐'), ('3', '😊'), ('4', '😄'), ('5', '🤩')],
        string='Satisfaction Rating')
    feedback = fields.Text(string='Feedback')

    # ─────────────────────────────────────────────────────────────────────────
    # Onchange
    # ─────────────────────────────────────────────────────────────────────────

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """
        When a contact is selected from res.partner:
        - Populate name from partner.name
        - Populate phone: prefer mobile → phone
        - Populate email
        Allows overriding afterwards — these are just defaults.
        If partner is cleared, fields are NOT wiped (keep what was typed).
        """
        if self.partner_id:
            self.name  = self.partner_id.name or self.name
            self.phone = (
                self.partner_id.mobile or
                self.partner_id.phone  or
                self.phone
            )
            self.email = self.partner_id.email or self.email

    # ─────────────────────────────────────────────────────────────────────────
    # Compute methods
    # ─────────────────────────────────────────────────────────────────────────

    @api.depends('token_number', 'department_id')
    def _compute_token_display(self):
        for rec in self:
            prefix = rec.department_id.code if rec.department_id else 'T'
            rec.token_display = f"{prefix}{rec.token_number:03d}"

    @api.depends('token_display', 'name')
    def _compute_display_name_field(self):
        for rec in self:
            rec.display_name = f"[{rec.token_display}] {rec.name}"

    @api.depends('priority', 'state')
    def _compute_color(self):
        color_map = {
            '3': 3,   # VIP → purple
            '2': 1,   # Urgent → red
            '1': 2,   # Priority → orange
            '0': 0,   # Normal → white/grey
        }
        state_color = {
            'in_service': 10,
            'done': 20,
            'no_show': 9,
            'cancelled': 9,
        }
        for rec in self:
            if rec.state in state_color:
                rec.color = state_color[rec.state]
            else:
                rec.color = color_map.get(rec.priority, 0)

    @api.depends('check_in_time', 'call_time', 'service_start_time', 'done_time')
    def _compute_durations(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.call_time and rec.check_in_time:
                rec.wait_duration = (
                    rec.call_time - rec.check_in_time).total_seconds() / 60
            elif rec.check_in_time and rec.state in ['waiting', 'called']:
                rec.wait_duration = (
                    now - rec.check_in_time).total_seconds() / 60
            else:
                rec.wait_duration = 0.0

            if rec.service_start_time and rec.done_time:
                rec.service_duration = (
                    rec.done_time - rec.service_start_time
                ).total_seconds() / 60
            elif rec.service_start_time and rec.state == 'in_service':
                rec.service_duration = (
                    now - rec.service_start_time).total_seconds() / 60
            else:
                rec.service_duration = 0.0

    @api.depends('sequence', 'department_id', 'priority')
    def _compute_estimated_wait(self):
        for rec in self:
            if rec.state not in ['waiting', 'called']:
                rec.estimated_wait = 0
                continue
            dept = rec.department_id
            avg_duration = dept.avg_service_duration if dept else 15
            # count people ahead
            domain = [
                ('room_id', '=', rec.room_id.id),
                ('state', 'in', ['waiting', 'called', 'in_service']),
                ('id', '!=', rec.id),
            ]
            if dept:
                domain.append(('department_id', '=', dept.id))
            ahead = self.search(domain).filtered(
                lambda l: (int(l.priority), -l.sequence, -l.token_number) >
                          (int(rec.priority), -rec.sequence, -rec.token_number)
            )
            rec.estimated_wait = len(ahead) * avg_duration

    @api.depends('check_in_time', 'estimated_wait')
    def _compute_is_late(self):
        now = fields.Datetime.now()
        threshold = 45  # minutes before considered overdue
        for rec in self:
            if rec.state in ['waiting', 'called'] and rec.check_in_time:
                waited = (now - rec.check_in_time).total_seconds() / 60
                rec.is_late = waited > threshold
            else:
                rec.is_late = False

    # ─────────────────────────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('token_number') or vals['token_number'] == 0:
                vals['token_number'] = self._get_next_token(
                    vals.get('room_id'), vals.get('department_id'))
        return super().create(vals_list)

    def _get_next_token(self, room_id, department_id):
        domain = [('room_id', '=', room_id)]
        if department_id:
            domain.append(('department_id', '=', department_id))
        # get max token for today
        today_start = fields.Datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        domain.append(('check_in_time', '>=', today_start))
        last = self.search(domain, order='token_number desc', limit=1)
        return (last.token_number + 1) if last else 1

    # ─────────────────────────────────────────────────────────────────────────
    # Actions / Buttons
    # ─────────────────────────────────────────────────────────────────────────

    def action_call(self):
        """Call the patient to the desk."""
        for rec in self:
            if rec.state not in ['waiting', 'called']:
                continue
            rec.write({
                'state': 'called',
                'call_time': fields.Datetime.now(),
                'call_count': rec.call_count + 1,
            })
            # Post message
            rec.message_post(
                body=_('Patient called: %s [%s]') % (rec.name, rec.token_display),
                message_type='notification',
            )
        return True

    def action_recall(self):
        """Re-call (second announcement)."""
        for rec in self:
            if rec.state != 'called':
                continue
            rec.write({
                'call_count': rec.call_count + 1,
                'call_time': fields.Datetime.now(),
            })

    def action_start_service(self):
        """Mark patient as In Service."""
        for rec in self:
            rec.write({
                'state': 'in_service',
                'service_start_time': fields.Datetime.now(),
            })

    def action_done(self):
        """Mark visit as complete."""
        for rec in self:
            rec.write({
                'state': 'done',
                'done_time': fields.Datetime.now(),
            })
            # Auto-call next if configured
            if rec.department_id and rec.department_id.auto_call_next:
                next_line = rec.department_id.get_next_waiting()
                if next_line:
                    next_line.action_call()

    def action_no_show(self):
        """Mark as No Show."""
        for rec in self:
            rec.write({'state': 'no_show'})

    def action_cancel(self):
        """Cancel the visit."""
        for rec in self:
            rec.write({'state': 'cancelled'})

    def action_requeue(self):
        """Re-queue a no-show or cancelled entry."""
        for rec in self:
            rec.write({
                'state': 'waiting',
                'call_time': False,
                'service_start_time': False,
                'done_time': False,
            })

    def action_call_next(self):
        """Call the next patient in queue for a given department."""
        self.ensure_one()
        if self.department_id:
            nxt = self.department_id.get_next_waiting()
        else:
            nxt = self.search([
                ('room_id', '=', self.room_id.id),
                ('state', '=', 'waiting'),
            ], limit=1, order='priority desc, sequence asc, token_number asc')
        if nxt:
            nxt.action_call()
            return nxt
        return False

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers for kanban/group
    # ─────────────────────────────────────────────────────────────────────────

    @api.model
    def _expand_states(self, states, domain):
        return [key for key, _val in STATE_SELECTION]

    # ─────────────────────────────────────────────────────────────────────────
    # Scheduled actions
    # ─────────────────────────────────────────────────────────────────────────

    @api.model
    def _auto_no_show(self):
        """Called by scheduled action — mark called entries older than 10min as No Show."""
        threshold = fields.Datetime.now() - timedelta(minutes=10)
        stale = self.search([
            ('state', '=', 'called'),
            ('call_time', '<', threshold),
        ])
        stale.action_no_show()
        _logger.info('Smart Waiting Room: %d entries marked as No Show.', len(stale))

    @api.model
    def _daily_reset(self):
        """Archive old done/cancelled entries at end of day."""
        yesterday = fields.Datetime.now() - timedelta(days=1)
        old = self.search([
            ('state', 'in', ['done', 'no_show', 'cancelled']),
            ('check_in_time', '<', yesterday),
        ])
        old.write({'active': False})
        _logger.info('Smart Waiting Room: %d entries archived.', len(old))

    active = fields.Boolean(default=True)
