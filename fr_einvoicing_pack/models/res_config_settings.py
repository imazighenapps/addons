# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fr_ereport_enabled = fields.Boolean(
        string="Enable E-Reporting Register",
        config_parameter="fr_einvoicing_pack.ereport_enabled",
        default=True,
    )
    fr_block_noncompliant = fields.Boolean(
        string="Block Non-Compliant Invoices",
        config_parameter="fr_einvoicing_pack.block_noncompliant",
        default=True,
        help="Prevent posting customer invoices that fail EN16931 validation.",
    )
    fr_chorus_url = fields.Char(
        string="Chorus Pro API URL",
        config_parameter="fr_einvoicing_pack.chorus_url",
        default="https://chorus-pro.gouv.fr:5443/service/factures/deposer/flux",
        help="Chorus Pro submission endpoint (test or production).",
    )
    fr_chorus_login = fields.Char(
        string="Chorus Pro Login",
        config_parameter="fr_einvoicing_pack.chorus_login",
    )
