# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class DocCredit(models.Model):
    _name = "doc.credit.desk"
    _description = "Crédit documentaire"
    _inherit = ["mail.thread"]
    _order = "issue_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one("res.partner", string="Bénéficiaire / Donneur d'ordre")
    issuing_bank = fields.Char(string="Banque émettrice")
    advising_bank = fields.Char(string="Banque notificatrice")
    amount = fields.Monetary(string="Montant", required=True)
    currency_id = fields.Many2one("res.currency", string="Devise", required=True, default=lambda self: self.env.company.currency_id)
    issue_date = fields.Date(string="Date d'ouverture", default=fields.Date.context_today)
    expiry_date = fields.Date(string="Date d'expiration")
    lc_type = fields.Selection([("import","Import"),("export","Export")], default="import", required=True)
    docs_required = fields.Text(string="Documents requis (checklist)")
    discrepancies = fields.Text(string="Discrepancies")
    state = fields.Selection([
        ("draft","Brouillon"),("open","Ouvert"),("presented","Présenté"),("accepted","Accepté"),
        ("discrepant","Discrepancies"),("settled","Dénoué"),("cancelled","Annulé")
    ], default="draft", tracking=True)
    notes = fields.Text(string="Notes")

    def action_open(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("doc.credit.desk") or "LC"
            rec.state = "open"
    def action_present(self): self.write({"state": "presented"})
    def action_accept(self): self.write({"state": "accepted"})
    def action_discrepant(self): self.write({"state": "discrepant"})
    def action_settle(self): self.write({"state": "settled"})
    def action_cancel(self): self.write({"state": "cancelled"})
