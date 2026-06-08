# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MergePartnerWizard(models.TransientModel):
    _name = 'merge.partner.wizard'
    _description = 'Merge Duplicate Partners Wizard'

    group_id = fields.Many2one('partner.duplicate.group', string='Duplicate Group')
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners to Merge',
    )
    master_partner_id = fields.Many2one(
        'res.partner',
        string='Master Record (to keep)',
        required=True,
        help='All data from other records will be moved to this one.',
    )
    duplicates_preview = fields.Html(
        string='Preview',
        compute='_compute_preview',
    )

    @api.depends('partner_ids', 'master_partner_id')
    def _compute_preview(self):
        for wiz in self:
            rows = ''
            for p in wiz.partner_ids:
                is_master = (p == wiz.master_partner_id)
                badge = (
                    '<span style="background:#d4edda;color:#155724;padding:2px 8px;'
                    'border-radius:4px;font-size:11px;">KEEP</span>'
                    if is_master else
                    '<span style="background:#f8d7da;color:#721c24;padding:2px 8px;'
                    'border-radius:4px;font-size:11px;">MERGE</span>'
                )
                rows += (
                    f'<tr>'
                    f'<td style="padding:6px 10px;">{badge}</td>'
                    f'<td style="padding:6px 10px;font-weight:{"600" if is_master else "400"};">'
                    f'{p.name or ""}</td>'
                    f'<td style="padding:6px 10px;color:#666;">{p.email or "—"}</td>'
                    f'<td style="padding:6px 10px;color:#666;">{p.phone or "—"}</td>'
                    f'<td style="padding:6px 10px;color:#666;">{p.vat or "—"}</td>'
                    f'</tr>'
                )
            wiz.duplicates_preview = (
                '<table style="width:100%;border-collapse:collapse;font-size:13px;">'
                '<thead><tr style="border-bottom:1px solid #dee2e6;">'
                '<th style="padding:6px 10px;text-align:left;">Action</th>'
                '<th style="padding:6px 10px;text-align:left;">Name</th>'
                '<th style="padding:6px 10px;text-align:left;">Email</th>'
                '<th style="padding:6px 10px;text-align:left;">Phone</th>'
                '<th style="padding:6px 10px;text-align:left;">VAT</th>'
                '</tr></thead>'
                f'<tbody>{rows}</tbody>'
                '</table>'
            )

    def action_merge(self):
        self.ensure_one()
        if not self.master_partner_id:
            raise UserError(_('Please select the master record to keep.'))
        if self.master_partner_id not in self.partner_ids:
            raise UserError(_('The master record must be one of the partners in the group.'))

        partners_to_merge = self.partner_ids - self.master_partner_id
        if not partners_to_merge:
            raise UserError(_('Nothing to merge: select at least 2 partners.'))

        master = self.master_partner_id
        _logger.info(
            'Merging %d partners into %s (id=%d)',
            len(partners_to_merge), master.name, master.id,
        )

        # Models that reference res.partner and must be rerouted
        PARTNER_FIELDS = [
            ('sale.order', 'partner_id'),
            ('sale.order', 'partner_invoice_id'),
            ('sale.order', 'partner_shipping_id'),
            ('account.move', 'partner_id'),
            ('purchase.order', 'partner_id'),
            ('stock.picking', 'partner_id'),
            ('crm.lead', 'partner_id'),
            ('helpdesk.ticket', 'partner_id'),
            ('project.task', 'partner_id'),
            ('res.partner', 'parent_id'),
        ]

        for partner in partners_to_merge:
            # 1. Reroute known relations
            for model_name, field_name in PARTNER_FIELDS:
                try:
                    Model = self.env[model_name]
                    records = Model.search([(field_name, '=', partner.id)])
                    if records:
                        records.write({field_name: master.id})
                        _logger.info(
                            '  Moved %d %s records (%s)',
                            len(records), model_name, field_name,
                        )
                except Exception:
                    pass  # model may not be installed

            # 2. Move chatter messages
            try:
                messages = self.env['mail.message'].search([
                    ('res_id', '=', partner.id),
                    ('model', '=', 'res.partner'),
                ])
                messages.write({'res_id': master.id})
            except Exception:
                pass

            # 3. Move followers
            try:
                followers = self.env['mail.followers'].search([
                    ('res_id', '=', partner.id),
                    ('res_model', '=', 'res.partner'),
                ])
                for follower in followers:
                    existing = self.env['mail.followers'].search([
                        ('res_id', '=', master.id),
                        ('res_model', '=', 'res.partner'),
                        ('partner_id', '=', follower.partner_id.id),
                    ])
                    if not existing:
                        follower.write({'res_id': master.id})
                    else:
                        follower.unlink()
            except Exception:
                pass

            # 4. Fill missing fields on master
            for fname in ['email', 'phone', 'vat', 'street',
                          'street2', 'city', 'zip', 'country_id', 'website']:
                master_val = getattr(master, fname, False)
                merge_val = getattr(partner, fname, False)
                if not master_val and merge_val:
                    try:
                        master.write({fname: merge_val})
                    except Exception:
                        pass

            # 5. Post a note on master
            master.message_post(
                body=_(
                    'Partner <strong>%s</strong> (id=%d) was merged into this record '
                    'by the Duplicate Detector module.'
                ) % (partner.name, partner.id),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            # 6. Archive the duplicate
            partner.write({'active': False})

        # 7. Mark group as merged
        if self.group_id:
            self.group_id.write({
                'state': 'merged',
                'master_partner_id': master.id,
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Merge successful'),
                'message': _(
                    '%d duplicates merged into %s.'
                ) % (len(partners_to_merge), master.name),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
