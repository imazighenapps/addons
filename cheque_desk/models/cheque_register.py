# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ChequeRegister(models.Model):
    _name = "cheque.register"
    _description = "Registre de chèques"
    _inherit = ["mail.thread"]
    _order = "deposit_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one("res.partner", string="Client", required=True)
    invoice_id = fields.Many2one("account.move", string="Facture", domain="[('move_type','=','out_invoice'),('partner_id','=',partner_id),('state','=','posted')]")
    cheque_number = fields.Char(string="N° chèque", required=True)
    bank_name = fields.Char(string="Banque émettrice")
    amount = fields.Monetary(string="Montant", required=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    deposit_date = fields.Date(string="Date de remise", default=fields.Date.context_today)
    due_date = fields.Date(string="Date valeur/encaissement prévu")
    clearing_date = fields.Date(string="Date d'encaissement")
    reject_date = fields.Date(string="Date de rejet")
    reject_reason = fields.Char(string="Motif de rejet")
    incident_count = fields.Integer(string="Incidents", default=0)
    state = fields.Selection([
        ("draft","Brouillon"),("deposited","Remis en banque"),("cleared","Encaissé"),("rejected","Rejeté/Impayé")
    ], default="draft", tracking=True)
    batch_ref = fields.Char(string="Référence lot de remise")
    notes = fields.Text(string="Notes")

    _sql_constraints = [("cheque_uniq", "unique(company_id, cheque_number, bank_name)", "Ce chèque est déjà enregistré.")]

    def action_deposit(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("cheque.register") or "CHQ"
            rec.state = "deposited"

    def action_clear(self):
        self.write({"state": "cleared", "clearing_date": fields.Date.context_today(self)})

    def action_reject(self):
        for rec in self:
            rec.incident_count += 1
            rec.write({"state": "rejected", "reject_date": fields.Date.context_today(self)})
