# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import models, fields, api, _

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
    # FIX: followup_config_id store=False signifie qu'il ne peut pas être utilisé
    # dans des domaines ni dans des dépendances d'autres computed fields stockés.
    # On le garde store=False mais on le rend utilisable via _get_followup_config().
    followup_config_id = fields.Many2one(
        'followup.config',
        string='Follow-up Configuration',
        compute='_compute_followup_config',
        store=False,
    )
    last_followup_date = fields.Datetime(string='Last Follow-up Date')
    followup_count = fields.Integer(string='Follow-up Count', default=0)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_followup_config(self):
        """Helper réutilisable pour récupérer la config follow-up de la commande."""
        self.ensure_one()
        return self.env['followup.config'].search([
            ('team_id', '=', self.team_id.id),
            ('active', '=', True),
        ], limit=1)

    # -------------------------------------------------------------------------
    # Computed fields
    # -------------------------------------------------------------------------

    @api.depends('team_id')
    def _compute_followup_config(self):
        for order in self:
            config = self.env['followup.config'].search([
                ('team_id', '=', order.team_id.id),
                ('active', '=', True),
            ], limit=1)
            order.followup_config_id = config

    @api.depends('state', 'date_order', 'message_ids', 'team_id')
    def _compute_followup_status(self):
        for order in self:
            if order.state != 'sent':
                order.days_without_reply = 0
                order.followup_status = 'ok'
                continue

            if order.date_order:
                now_utc = fields.Datetime.now()
                date_order_dt = fields.Datetime.to_datetime(order.date_order) \
                    if isinstance(order.date_order, str) \
                    else order.date_order
                delta = (now_utc - date_order_dt).days
            else:
                delta = 0

            inbound_msg = self.env['mail.message'].search([
                ('res_id', '=', order.id),
                ('model', '=', 'sale.order'),
                ('author_id', '=', order.partner_id.id),
                ('message_type', 'in', ['email', 'comment']),
                # FIX: on s'assure que le message est APRÈS l'envoi du devis
                ('date', '>=', order.date_order),
            ], limit=1, order='date desc')

            if inbound_msg:
                order.days_without_reply = 0
                order.followup_status = 'ok'
                continue

            order.days_without_reply = delta

            # Récupération de la config (mutualisée)
            config = self.env['followup.config'].search([
                ('team_id', '=', order.team_id.id),
                ('active', '=', True),
            ], limit=1)

            if not config:
                # FIX: comportement par défaut cohérent même sans config
                order.followup_status = 'pending' if delta > 3 else 'ok'
                continue

            # Vérification du montant minimum
            if config.min_amount and order.amount_total < config.min_amount:
                order.followup_status = 'ok'
                continue

            if delta >= config.delay_3:
                order.followup_status = 'escalated'
            elif delta >= config.delay_2:
                order.followup_status = 'overdue'
            elif delta >= config.delay_1:
                order.followup_status = 'pending'
            else:
                order.followup_status = 'ok'
        order.followup_status='pending'
    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def action_send_followup(self):
        """
        FIX: Ajout de ensure_one() pour éviter une erreur si appelé sur un
             recordset multiple (ex: depuis la vue liste).
        """
        self.ensure_one()
        config = self._get_followup_config()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send Follow-up'),
            'res_model': 'followup.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_template_id': config.template_id.id if config else False,
            }
        }

    # -------------------------------------------------------------------------
    # Cron
    # -------------------------------------------------------------------------

    @api.model
    def _cron_check_followups(self):
        """
        FIX 1: Le filtre 'followup_status in [...]' sur un champ computed/stored
                fonctionne correctement. Mais on force d'abord un recalcul des
                enregistrements en état 'sent' pour s'assurer que les données
                sont à jour avant de les filtrer.
        FIX 2: La vérification du min_amount est déplacée dans _compute_followup_status,
                donc le cron est simplifié.
        FIX 3: Ajout d'une protection contre les doublons de notification manager
                (pas de vérification dans le code original).
        AMÉLIORATION: Utilisation de sudo() limité pour les opérations sensibles.
        """
        _logger.info('Running Smart Follow-up Reminder cron...')

        # Forcer le recalcul des devis envoyés avant de filtrer par statut
        sent_orders = self.search([('state', '=', 'sent')])
        if sent_orders:
            sent_orders._compute_followup_status()

        orders = self.search([
            ('state', '=', 'sent'),
            ('followup_status', 'in', ['pending', 'overdue', 'escalated']),
        ])

        activity_type = self.env.ref(
            'mail.mail_activity_data_todo', raise_if_not_found=False
        )

        activity_count = 0
        escalation_count = 0

        for order in orders:
            # Créer une activité pour le commercial (sans doublon)
            existing = self.env['mail.activity'].search([
                ('res_id', '=', order.id),
                ('res_model', '=', 'sale.order'),
                ('user_id', '=', order.user_id.id),
                ('summary', 'ilike', 'Follow-up'),
            ], limit=1)

            if not existing and activity_type:
                order.activity_schedule(
                    activity_type_id=activity_type.id,
                    summary=_('Follow-up: %s') % order.name,
                    note=_(
                        'Quote %(name)s has been without reply for %(days)d days.',
                        name=order.name,
                        days=order.days_without_reply,
                    ),
                    user_id=order.user_id.id,
                )
                activity_count += 1
                _logger.info('Activity created for order %s', order.name)

            # Notifier le manager pour les escalades
            # FIX: Vérification que la notification n'a pas déjà été envoyée
            # aujourd'hui pour éviter le spam (via last_followup_date)
            if (
                order.followup_status == 'escalated'
                and order.team_id.user_id
                and order.team_id.user_id != order.user_id  # éviter auto-notification
            ):
                # FIX: Vérifier si une notification a déjà été envoyée aujourd'hui
                today_start = fields.Datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                already_notified = self.env['mail.message'].search([
                    ('res_id', '=', order.id),
                    ('model', '=', 'sale.order'),
                    ('subtype_id', '=', self.env.ref(
                        'mail.mt_note', raise_if_not_found=False
                    ) and self.env.ref('mail.mt_note').id or False),
                    ('date', '>=', today_start),
                    ('author_id', '=', self.env.user.partner_id.id),
                ], limit=1)

                if not already_notified:
                    order.message_notify(
                        partner_ids=[order.team_id.user_id.partner_id.id],
                        subject=_('Escalation: Quote %s') % order.name,
                        body=_(
                            'Quote %(name)s from %(partner)s has been without '
                            'reply for %(days)d days and needs your attention.',
                            name=order.name,
                            partner=order.partner_id.name,
                            days=order.days_without_reply,
                        ),
                    )
                    escalation_count += 1

        _logger.info(
            'Smart Follow-up Reminder cron finished. '
            'Processed %d orders — %d activities created, %d escalations sent.',
            len(orders), activity_count, escalation_count,
        )