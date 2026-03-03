# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class FollowupWizard(models.TransientModel):
    _name = 'followup.wizard'
    _description = 'Follow-up Reminder Wizard'

    order_id = fields.Many2one('sale.order', string='Quotation', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        related='order_id.partner_id', readonly=True
    )
    template_id = fields.Many2one(
        'mail.template', string='Email Template',
        domain=[('model', '=', 'sale.order')]
    )
    subject = fields.Char(string='Subject')
    body_html = fields.Html(string='Message Body')

    @api.onchange('template_id', 'order_id')
    def _onchange_template(self):
        if self.template_id and self.order_id:
            lang_map = self.template_id._render_lang([self.order_id.id])
            lang = lang_map.get(self.order_id.id)
            _logger.warning("lang => %s", lang)
            template = self.template_id.with_context(lang=lang)
            subject_map = template._render_field('subject', [self.order_id.id])
            body_map = template._render_field('body_html', [self.order_id.id])
            _logger.warning("\n ok ok body_map=>%s",body_map)
            self.subject = subject_map.get(self.order_id.id, '')
            self.body_html = body_map.get(self.order_id.id, '')
            


    def action_send(self):
        self.ensure_one()
        if not self.order_id:
            return
        self.order_id.message_post(
            body=self.body_html,
            subject=self.subject,
            message_type='email',
            subtype_xmlid='mail.mt_comment',
            partner_ids=[self.partner_id.id],
        )
        self.order_id.sudo().write({
            'last_followup_date': fields.Datetime.now(),
            'followup_count': self.order_id.followup_count + 1,
        })
        _logger.info('Follow-up sent for order %s (count: %d)',
                     self.order_id.name, self.order_id.followup_count)
        return {'type': 'ir.actions.act_window_close'}
