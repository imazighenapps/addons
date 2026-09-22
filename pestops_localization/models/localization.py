from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    pestops_default_language_id = fields.Many2one(
        "res.lang",
        string="PestOps Default Language",
        help="Default language used by PestOps documents when the customer language is not set.",
    )
    pestops_default_country_id = fields.Many2one(
        "res.country",
        string="PestOps Default Country",
        help="Default business country context used by PestOps document profiles.",
    )
    pestops_default_currency_id = fields.Many2one(
        "res.currency",
        string="PestOps Default Currency",
        help="Default reporting currency. Accounting remains managed by Odoo Accounting.",
    )
    pestops_report_timezone = fields.Selection(
        selection="_tz_get",
        string="Report Timezone",
        default="UTC",
        help="Timezone used when rendering PestOps timestamps in localized documents.",
    )
    pestops_enable_bilingual_reports = fields.Boolean(
        string="Enable Bilingual Reports",
        default=False,
        help="Allow a PestOps report profile to display a secondary language label set.",
    )

    @api.model
    def _tz_get(self):
        return [(tz, tz) for tz in self.env["res.lang"]._fields.get("name", [])] if False else [
            ("UTC", "UTC"),
            ("Africa/Algiers", "Africa/Algiers"),
            ("Europe/Paris", "Europe/Paris"),
            ("Europe/Madrid", "Europe/Madrid"),
            ("Europe/London", "Europe/London"),
            ("Asia/Dubai", "Asia/Dubai"),
            ("Asia/Riyadh", "Asia/Riyadh"),
        ]


class ResPartner(models.Model):
    _inherit = "res.partner"

    pestops_document_language_id = fields.Many2one(
        "res.lang",
        string="PestOps Document Language",
        help="Language preferred for PestOps reports and certificates.",
    )
    pestops_document_profile_id = fields.Many2one(
        "pest.document.profile",
        string="PestOps Document Profile",
        help="Profile used for PestOps customer-facing documents.",
    )
