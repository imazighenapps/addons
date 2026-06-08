# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    duplicate_group_ids = fields.Many2many(
        'partner.duplicate.group',
        'partner_duplicate_group_rel',
        'partner_id',
        'group_id',
        string='Duplicate Groups',
    )
    duplicate_count = fields.Integer(
        string='Duplicates',
        compute='_compute_duplicate_count',
    )
    is_duplicate = fields.Boolean(
        string='Has Duplicates',
        compute='_compute_duplicate_count',
        store=False,
    )

    @api.depends('duplicate_group_ids', 'duplicate_group_ids.state')
    def _compute_duplicate_count(self):
        for partner in self:
            pending = partner.duplicate_group_ids.filtered(
                lambda g: g.state == 'pending'
            )
            count = sum(
                len(g.partner_ids) - 1
                for g in pending
            )
            partner.duplicate_count = count
            partner.is_duplicate = count > 0

    def action_view_duplicates(self):
        self.ensure_one()
        pending_groups = self.duplicate_group_ids.filtered(
            lambda g: g.state == 'pending'
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('Duplicate Groups'),
            'res_model': 'partner.duplicate.group',
            'view_mode': 'list,form',
            'domain': [('id', 'in', pending_groups.ids)],
        }
