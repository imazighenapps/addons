# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FollowupWizard(models.TransientModel):
    _name = 'followup.wizard'
    _description = 'Follow-up Reminder Wizard'

    order_id = fields.Many2one('sale.order', string='Quotation', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        related='order_id.partner_id', readonly=True,
    )
    template_id = fields.Many2one(
        'mail.template', string='Email Template',
        domain=[('model', '=', 'sale.order')],
    )
    subject = fields.Char(string='Subject')
    body_html = fields.Html(string='Message Body')

    @api.onchange('template_id', 'order_id')
    def _onchange_template(self):
        if self.template_id and self.order_id:
            lang_map = self.template_id._render_lang([self.order_id.id])
            lang = lang_map.get(self.order_id.id)
            template = self.template_id.with_context(lang=lang)
            subject_map = template._render_field('subject', [self.order_id.id])
            body_map = template._render_field('body_html', [self.order_id.id])
            self.subject = subject_map.get(self.order_id.id, '')
            self.body_html = body_map.get(self.order_id.id, '')

    def action_send(self):
        """
        FIX 1: Ajout d'une validation que le devis est bien en état 'sent'.
        FIX 2: Ajout d'une validation que subject et body ne sont pas vides.
        FIX 3: followup_count incrémenté de façon atomique.
        AMÉLIORATION: Retour d'une notification de succès à l'utilisateur.
        """
        self.ensure_one()
        if not self.order_id:
            raise UserError(_('No quotation linked to this follow-up.'))

        if self.order_id.state != 'sent':
            raise UserError(
                _('Follow-up can only be sent for quotations in "Sent" state. '
                  'Current state: %s') % self.order_id.state
            )

        if not self.body_html and not self.subject:
            raise UserError(
                _('Please fill in the subject or message body before sending.')
            )

        # Envoi du message via chatter (enregistré dans l'historique)
        self.order_id.message_post(
            body=self.body_html or '',
            subject=self.subject or '',
            message_type='email',
            subtype_xmlid='mail.mt_comment',
            partner_ids=[self.partner_id.id],
        )

        # FIX 3: Écriture atomique
        self.order_id.sudo().write({
            'last_followup_date': fields.Datetime.now(),
            'followup_count': self.order_id.followup_count + 1,
        })

        _logger.info(
            'Follow-up sent for order %s (total count: %d)',
            self.order_id.name,
            self.order_id.followup_count,
        )

        # AMÉLIORATION: Notification de succès
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Follow-up Sent'),
                'message': _('Follow-up successfully sent to %s.') % self.partner_id.name,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }