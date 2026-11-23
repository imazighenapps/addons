# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FxForward(models.Model):
    _name = "fx.forward.desk"
    _description = "Contrat à terme de change"
    _inherit = ["mail.thread"]
    _order = "maturity_date asc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", string="Devise couverte", required=True)
    counter_currency_id = fields.Many2one("res.currency", string="Devise de contrepartie", required=True, default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(string="Montant couvert", required=True, currency_field="currency_id")
    forward_rate = fields.Float(string="Taux à terme", required=True, digits=(12,6))
    spot_rate = fields.Float(string="Taux spot à l'ouverture", digits=(12,6))
    maturity_date = fields.Date(string="Échéance", required=True)
    partner_id = fields.Many2one("res.partner", string="Contrepartie bancaire")
    invoice_id = fields.Many2one("account.move", string="Créance/Dette couverte")
    settlement_rate = fields.Float(string="Taux au dénouement", digits=(12,6))
    hedge_gain_loss = fields.Monetary(string="Gain/Perte de couverture", compute="_compute_gain_loss", store=True, currency_field="counter_currency_id")
    state = fields.Selection([("draft","Brouillon"),("open","Ouvert"),("settled","Dénoué"),("cancelled","Annulé")], default="draft", tracking=True)
    notes = fields.Text(string="Notes")

    @api.depends("amount", "forward_rate", "settlement_rate")
    def _compute_gain_loss(self):
        for rec in self:
            if rec.settlement_rate and rec.forward_rate:
                rec.hedge_gain_loss = rec.amount * (rec.settlement_rate - rec.forward_rate)
            else:
                rec.hedge_gain_loss = 0.0

    def action_open(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("fx.forward.desk") or "FXFWD"
            rec.state = "open"

    def action_settle(self):
        for rec in self:
            if not rec.settlement_rate:
                raise UserError(_("Renseignez le taux au dénouement."))
            rec.state = "settled"

    def action_cancel(self):
        self.write({"state": "cancelled"})
