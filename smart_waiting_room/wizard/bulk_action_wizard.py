# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WaitingRoomBulkAction(models.TransientModel):
    _name = 'waiting.room.bulk.action'
    _description = 'Bulk Action on Queue'

    action = fields.Selection([
        ('call', 'Call All Selected'),
        ('done', 'Mark as Done'),
        ('no_show', 'Mark as No Show'),
        ('cancel', 'Cancel'),
        ('requeue', 'Re-queue'),
    ], string='Action', required=True, default='call')

    line_ids = fields.Many2many(
        'waiting.room.line', string='Entries')

    def action_apply(self):
        self.ensure_one()
        method_map = {
            'call': 'action_call',
            'done': 'action_done',
            'no_show': 'action_no_show',
            'cancel': 'action_cancel',
            'requeue': 'action_requeue',
        }
        method = method_map.get(self.action)
        if method:
            getattr(self.line_ids, method)()
        return {'type': 'ir.actions.act_window_close'}
