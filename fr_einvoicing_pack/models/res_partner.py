# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .fr_tools import (
    clean_identifier,
    is_siren,
    is_siret,
    siren_from_siret,
    is_fr_vat,
)


class ResPartner(models.Model):
    _inherit = "res.partner"

    fr_siren = fields.Char(
        string="SIREN",
        help="9-digit French company identifier. Must pass the Luhn checksum.",
    )
    fr_siret = fields.Char(
        string="SIRET",
        help="14-digit French establishment identifier. Must pass the Luhn checksum.",
    )
    fr_einvoicing_ready = fields.Boolean(
        string="E-Invoicing Ready",
        compute="_compute_fr_einvoicing_ready",
        store=True,
        help="True when this partner carries every mandatory e-invoicing identifier.",
    )
    fr_einvoicing_issues = fields.Text(
        string="E-Invoicing Issues",
        compute="_compute_fr_einvoicing_ready",
        store=True,
    )

    @api.constrains("fr_siren", "fr_siret")
    def _check_fr_identifiers(self):
        for partner in self:
            siren = clean_identifier(partner.fr_siren)
            if siren and not is_siren(siren):
                raise ValidationError(
                    _("Invalid SIREN '%s': 9 digits with a valid Luhn checksum are required.") % partner.fr_siren
                )
            siret = clean_identifier(partner.fr_siret)
            if siret and not is_siret(siret):
                raise ValidationError(
                    _("Invalid SIRET '%s': 14 digits with a valid Luhn checksum are required.") % partner.fr_siret
                )
            if siren and siret and not siret.startswith(siren):
                raise ValidationError(
                    _("The SIRET must start with the partner SIREN.")
                )

    @api.depends("fr_siren", "fr_siret", "vat", "country_id", "is_company")
    @api.onchange("fr_siret")
    def _onchange_fr_siret(self):
        for partner in self:
            siren = siren_from_siret(partner.fr_siret)
            if siren and not partner.fr_siren:
                partner.fr_siren = siren

    @api.depends("fr_siren", "fr_siret", "vat", "country_id", "is_company")
    def _compute_fr_einvoicing_ready(self):
        for partner in self:
            issues = []
            if partner.is_company and partner.country_id and partner.country_id.code == "FR":
                if not is_siren(partner.fr_siren):
                    issues.append(_("Missing or invalid SIREN."))
                if partner.vat and not is_fr_vat(partner.vat):
                    issues.append(_("Invalid French VAT number (expected FR + key + SIREN)."))
            partner.fr_einvoicing_issues = "\n".join(issues)
            partner.fr_einvoicing_ready = not issues
