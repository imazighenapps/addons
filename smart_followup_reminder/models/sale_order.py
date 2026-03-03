# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    days_without_reply = fields.Integer(
        string='Days Without Reply',
        compute='_compute_followup_status',
        store=True,
    )
    followup_status = fields.Selection([
        ('ok', 'OK'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
        ('escalated', 'Escalated'),
    ], string='Follow-up Status',
        compute='_compute_followup_status',
        store=True,
        default='ok',
    )
    followup_config_id = fields.Many2one(
        'followup.config',
        string='Follow-up Configuration',
        compute='_compute_followup_config',
        store=False,
    )
    last_followup_date = fields.Datetime(string='Last Follow-up Date')
    followup_count = fields.Integer(string='Follow-up Count', default=0)

    @api.depends('team_id')
    def _compute_followup_config(self):
        for order in self:
            config = self.env['followup.config'].search([
                ('team_id', '=', order.team_id.id),
                ('active', '=', True)
            ], limit=1)
            order.followup_config_id = config

    @api.depends('state', 'date_order', 'message_ids')
    def _compute_followup_status(self):
        for order in self:
            if order.state != 'sent':
                order.days_without_reply = 0
                order.followup_status = 'ok'
                continue

            # Count days since order was sent
            if order.date_order:
                delta = (datetime.now() - fields.Datetime.from_string(str(order.date_order))).days
            else:
                delta = 0

            # Check if there is an inbound message from the partner
            inbound_msg = self.env['mail.message'].search([
                ('res_id', '=', order.id),
                ('model', '=', 'sale.order'),
                ('author_id', '=', order.partner_id.id),
                ('message_type', 'in', ['email', 'comment']),
            ], limit=1, order='date desc')

            if inbound_msg:
                order.days_without_reply = 0
                order.followup_status = 'ok'
                continue

            order.days_without_reply = delta
            config = self.env['followup.config'].search([
                ('team_id', '=', order.team_id.id),
                ('active', '=', True)
            ], limit=1)

            if not config:
                order.followup_status = 'pending' if delta > 3 else 'ok'
                continue

            if delta >= config.delay_3:
                order.followup_status = 'escalated'
            elif delta >= config.delay_2:
                order.followup_status = 'overdue'
            elif delta >= config.delay_1:
                order.followup_status = 'pending'
            else:
                order.followup_status = 'ok'


    def action_send_followup(self):
     
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send Follow-up'),
            'res_model': 'followup.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_template_id': self.followup_config_id.template_id.id if self.followup_config_id else False,
            }
        }

    @api.model
    def _cron_check_followups(self):
        _logger.info('Running Smart Follow-up Reminder cron...')
        orders = self.search([
            ('state', '=', 'sent'),
            ('followup_status', 'in', ['pending', 'overdue', 'escalated']),
        ])
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        for order in orders:
            config = order.followup_config_id
            if config and order.amount_total < config.min_amount:
                continue

            # Create activity for salesperson
            existing = self.env['mail.activity'].search([
                ('res_id', '=', order.id),
                ('res_model', '=', 'sale.order'),
                ('user_id', '=', order.user_id.id),
                ('summary', 'ilike', _('Follow-up')),
            ], limit=1)
            if not existing and activity_type:
                order.activity_schedule(
                    activity_type_id=activity_type.id,
                    summary=_('Follow-up: %s') % order.name,
                    note=_('Quote %s has been without reply for %d days.') % (
                        order.name, order.days_without_reply
                    ),
                    user_id=order.user_id.id,
                )
                _logger.info('Activity created for order %s', order.name)

            # Notify manager on escalated
            if order.followup_status == 'escalated' and order.team_id.user_id:
                order.message_notify(
                    partner_ids=[order.team_id.user_id.partner_id.id],
                    subject=_('Escalation: Quote %s') % order.name,
                    body=_('Quote %s from %s has been without reply for %d days and needs your attention.') % (
                        order.name, order.partner_id.name, order.days_without_reply
                    ),
                )
        _logger.info('Smart Follow-up Reminder cron finished. Processed %d orders.', len(orders))
