from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestDocumentProfile(models.Model):
    _name = "pest.document.profile"
    _description = "PestOps Document Profile"
    _order = "company_id, sequence, name"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        help="Country context only. Fiscal and legal rules remain managed by Odoo.",
    )
    language_id = fields.Many2one(
        "res.lang",
        string="Primary Language",
        required=True,
        default=lambda self: self.env.lang and self.env["res.lang"].search(
            [("code", "=", self.env.lang)], limit=1
        ),
    )
    secondary_language_id = fields.Many2one(
        "res.lang",
        string="Secondary Language",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Display Currency",
        default=lambda self: self.env.company.currency_id,
    )

    service_title = fields.Char(
        string="Service Title",
        default="Pest Control Service",
        translate=True,
    )
    treatment_title = fields.Char(
        string="Treatment Title",
        default="Treatment Certificate",
        translate=True,
    )
    inspection_title = fields.Char(
        string="Inspection Title",
        default="Inspection Report",
        translate=True,
    )
    footer_text = fields.Text(
        string="Footer Text",
        translate=True,
    )
    legal_notice = fields.Text(
        string="Legal / Compliance Notice",
        translate=True,
        help="Informational text only; do not use this field to encode legal rules.",
    )
    contact_text = fields.Text(
        string="Contact Text",
        translate=True,
    )
    show_currency = fields.Boolean(default=True)
    show_country = fields.Boolean(default=True)
    show_customer_language = fields.Boolean(default=True)
    bilingual = fields.Boolean(
        compute="_compute_bilingual",
        store=True,
    )

    _sql_constraints = [
        (
            "pest_document_profile_company_name_uniq",
            "unique(company_id, name)",
            "Document profile name must be unique per company.",
        ),
    ]

    @api.depends("secondary_language_id")
    def _compute_bilingual(self):
        for rec in self:
            rec.bilingual = bool(rec.secondary_language_id)

    @api.constrains("company_id", "country_id")
    def _check_country(self):
        for rec in self:
            if rec.country_id and rec.company_id.country_id and rec.country_id != rec.company_id.country_id:
                # This is informational, not a blocker for multi-country operations.
                continue

    def get_report_context(self, partner=False):
        self.ensure_one()
        customer_lang = (
            partner.pestops_document_language_id
            if partner and partner.pestops_document_language_id
            else self.language_id
        )
        return {
            "language": customer_lang.code if customer_lang else self.env.lang,
            "secondary_language": self.secondary_language_id.code if self.secondary_language_id else False,
            "currency": self.currency_id.name if self.currency_id else False,
            "country": self.country_id.name if self.country_id else False,
            "service_title": self.service_title,
            "treatment_title": self.treatment_title,
            "inspection_title": self.inspection_title,
            "footer_text": self.footer_text,
            "legal_notice": self.legal_notice,
            "contact_text": self.contact_text,
            "bilingual": self.bilingual,
        }


class PestVisit(models.Model):
    _inherit = "pest.visit"

    document_profile_id = fields.Many2one(
        "pest.document.profile",
        string="Document Profile",
        help="Localized document profile used for this intervention's reports.",
    )

    def _get_pestops_document_profile(self):
        self.ensure_one()
        return (
            self.document_profile_id
            or self.partner_id.pestops_document_profile_id
            or self.env.company.pestops_default_language_id
            and self.env["pest.document.profile"].search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("language_id", "=", self.env.company.pestops_default_language_id.id),
                    ("active", "=", True),
                ],
                order="sequence,id",
                limit=1,
            )
            or self.env["pest.document.profile"].search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("active", "=", True),
                ],
                order="sequence,id",
                limit=1,
            )
        )
