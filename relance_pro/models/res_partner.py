# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    dunning_paused = fields.Boolean(
        string="Pause Dunning",
        help="Stop the dunning ladder for this customer.")
    dunning_pause_until = fields.Date(
        string="Paused Until",
        help="When set, the dunning ladder resumes after this date.")
    dunning_note = fields.Text(string="Dunning Note")
