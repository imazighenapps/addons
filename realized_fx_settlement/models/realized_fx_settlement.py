# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class RealizedFxSettlement(models.Model):
    _name = "realized.fx.settlement"
    _description = "Écart de change réalisé"
    _inherit = ["mail.thread"]
    _order = "settlement_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one("account.move", string="Facture / pièce", required=True,
        domain="[('state','=','posted'),('company_id','=',company_id)]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    currency_id = fields.Many2one(related="invoice_id.currency_id", store=True)
    company_currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    settlement_date = fields.Date(string="Date de règlement", default=fields.Date.context_today)
    invoice_rate = fields.Float(string="Taux facture", digits=(12,6), required=True)
    settlement_rate = fields.Float(string="Taux règlement", digits=(12,6), required=True)
    amount_currency = fields.Monetary(string="Montant devise", required=True, currency_field="currency_id")
    fx_gain_loss = fields.Monetary(string="Gain/Perte de change", compute="_compute_fx", store=True, currency_field="company_currency_id")
    skip_threshold = fields.Monetary(string="Seuil de saut", default=0.0, currency_field="company_currency_id")
    skipped = fields.Boolean(string="Écart ignoré (seuil)", compute="_compute_fx", store=True)
    state = fields.Selection([("draft","Brouillon"),("computed","Calculé"),("posted","Comptabilisé")], default="draft", tracking=True)
    notes = fields.Text(string="Notes / audit")

    @api.depends("amount_currency", "invoice_rate", "settlement_rate", "skip_threshold")
    def _compute_fx(self):
        for rec in self:
            base_inv = rec.amount_currency / (rec.invoice_rate or 1.0)
            base_set = rec.amount_currency / (rec.settlement_rate or 1.0)
            diff = base_set - base_inv
            rec.fx_gain_loss = diff
            rec.skipped = abs(diff) < (rec.skip_threshold or 0.0) if rec.skip_threshold else False

    def action_compute(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("realized.fx.settlement") or "FXR"
            rec.state = "computed"
            rec.notes = (rec.notes or "") + ("\n[%s] Gain/Perte: %.2f" % (fields.Datetime.now(), rec.fx_gain_loss))

    def action_post(self):
        self.write({"state": "posted"})
