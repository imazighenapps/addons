# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreditInsuranceCase(models.Model):
    _name = "credit.insurance.case"
    _description = "Dossier assurance-crédit"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    insurer_name = fields.Char(string="Assureur", required=True)
    partner_id = fields.Many2one("res.partner", string="Acheteur assuré", required=True)
    limit_amount = fields.Monetary(string="Plafond assureur", required=True)
    used_amount = fields.Monetary(string="Encours déclaré", default=0.0)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    monthly_sales = fields.Monetary(string="Ventes déclarées (mois)")
    claim_amount = fields.Monetary(string="Montant sinistre")
    indemnity_amount = fields.Monetary(string="Indemnité reçue")
    declaration_date = fields.Date(string="Date déclaration ventes")
    claim_date = fields.Date(string="Date sinistre")
    over_limit = fields.Boolean(string="Plafond dépassé", compute="_compute_over", store=True)
    state = fields.Selection([
        ("draft","Brouillon"),("declared","Déclaré"),("claim","Sinistre déclaré"),("indemnified","Indemnisé"),("closed","Clos")
    ], default="draft", tracking=True)
    notes = fields.Text(string="Notes / pièces")

    @api.depends("limit_amount", "used_amount", "monthly_sales")
    def _compute_over(self):
        for rec in self:
            rec.over_limit = (rec.used_amount or 0.0) + (rec.monthly_sales or 0.0) > (rec.limit_amount or 0.0)

    def action_declare(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("credit.insurance.case") or "CINS"
            rec.state = "declared"
            if not rec.declaration_date:
                rec.declaration_date = fields.Date.context_today(self)
            rec.used_amount = (rec.used_amount or 0.0) + (rec.monthly_sales or 0.0)

    def action_claim(self):
        if not self.claim_amount:
            raise UserError(_("Renseignez le montant du sinistre."))
        self.write({"state": "claim", "claim_date": fields.Date.context_today(self)})

    def action_indemnify(self):
        self.write({"state": "indemnified"})

    def action_close(self):
        self.write({"state": "closed"})
