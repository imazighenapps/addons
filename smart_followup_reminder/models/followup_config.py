# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class FollowupConfig(models.Model):
    _name = 'followup.config'
    _description = 'Follow-up Configuration'
    _rec_name = 'name'
    # FIX: Ajout d'un ordre par défaut pour un affichage cohérent
    _order = 'team_id, name'

    name = fields.Char(string='Configuration Name', required=True)
    team_id = fields.Many2one(
        'crm.team', string='Sales Team', required=True, ondelete='cascade'
    )
    delay_1 = fields.Integer(
        string='Days Before 1st Reminder', default=3,
        help='Number of days without reply before sending the first reminder.'
    )
    delay_2 = fields.Integer(
        string='Days Before 2nd Reminder', default=5,
        help='Number of days without reply before sending the second reminder.'
    )
    delay_3 = fields.Integer(
        string='Days Before Manager Escalation', default=7,
        help='Number of days without reply before escalating to the manager.'
    )
    min_amount = fields.Float(
        string='Minimum Amount', default=0.0,
        help='Minimum order amount to trigger follow-up reminders.'
    )
    template_id = fields.Many2one(
        'mail.template', string='Email Template',
        domain=[('model', '=', 'sale.order')]
    )
    active = fields.Boolean(string='Active', default=True)

    # FIX CRITIQUE: _() ne peut pas être appelé au niveau de la classe (hors méthode).
    # En Odoo, les messages de contrainte SQL doivent être des chaînes brutes
    # ou utiliser une lambda. Utilisation d'une chaîne statique ici (bonne pratique).
    _sql_constraints = [
        (
            'unique_team',
            'UNIQUE(team_id)',
            'A configuration already exists for this sales team.'
        )
    ]

    @api.constrains('delay_1', 'delay_2', 'delay_3')
    def _check_delays(self):
        """FIX/AMÉLIORATION: Valider la cohérence des délais."""
        for rec in self:
            if rec.delay_1 <= 0 or rec.delay_2 <= 0 or rec.delay_3 <= 0:
                raise models.ValidationError(
                    _('All delay values must be strictly positive.')
                )
            if not (rec.delay_1 < rec.delay_2 < rec.delay_3):
                raise models.ValidationError(
                    _('Delays must be in increasing order: '
                      '1st Reminder < 2nd Reminder < Manager Escalation.')
                )

    @api.constrains('min_amount')
    def _check_min_amount(self):
        """AMÉLIORATION: Empêcher un montant minimum négatif."""
        for rec in self:
            if rec.min_amount < 0:
                raise models.ValidationError(
                    _('Minimum amount cannot be negative.')
                )