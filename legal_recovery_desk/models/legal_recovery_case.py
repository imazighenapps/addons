# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class LegalRecoveryCase(models.Model):
    _name = "legal.recovery.case"
    _description = "Contentieux de recouvrement"
    _inherit = ["mail.thread"]
    _order = "opened_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one("account.move", string="Facture", required=True,
        domain="[('move_type','=','out_invoice'),('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    amount_claimed = fields.Monetary(string="Montant réclamé", required=True)
    fees_amount = fields.Monetary(string="Frais judiciaires / honoraires")
    recovered_amount = fields.Monetary(string="Montant recouvré")
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    opened_date = fields.Date(string="Date d'ouverture", default=fields.Date.context_today)
    hearing_date = fields.Date(string="Date d'audience")
    procedure_step = fields.Selection([
        ("injunction","Injonction de payer"),("bailiff","Huissier"),("hearing","Audience"),("judgment","Jugement"),("execution","Exécution")
    ], string="Étape procédurale", default="injunction", tracking=True)
    bailiff_name = fields.Char(string="Huissier / Avocat")
    state = fields.Selection([("draft","Brouillon"),("ongoing","En cours"),("won","Gagné"),("lost","Perdu"),("closed","Clos")], default="draft", tracking=True)
    notes = fields.Text(string="Notes")

    def action_start(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("legal.recovery.case") or "LEGAL"
            rec.state = "ongoing"

    def action_win(self):
        self.write({"state": "won"})
    def action_lose(self):
        self.write({"state": "lost"})
    def action_close(self):
        self.write({"state": "closed"})
