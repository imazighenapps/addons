# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CashPoolingTransfer(models.Model):
    _name = "cash.pooling.transfer"
    _description = "Mouvement de cash pooling"
    _inherit = ["mail.thread"]
    _order = "transfer_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", string="Société source", required=True, default=lambda self: self.env.company)
    target_company_id = fields.Many2one("res.company", string="Société cible", required=True)
    transfer_date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    amount = fields.Monetary(string="Montant d'alignement", required=True)
    interest_rate = fields.Float(string="Taux d'intérêt annuel (%)", default=2.0)
    interest_amount = fields.Monetary(string="Intérêts", compute="_compute_interest", store=True)
    net_amount = fields.Monetary(string="Montant net", compute="_compute_interest", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    direction = fields.Selection([("to_pool","Vers compte technique"),("from_pool","Depuis compte technique")], required=True, default="to_pool")
    state = fields.Selection([("draft","Brouillon"),("computed","Calculé"),("posted","Comptabilisé"),("cancelled","Annulé")], default="draft", tracking=True)
    notes = fields.Text(string="Notes / justificatif")

    @api.depends("amount", "interest_rate")
    def _compute_interest(self):
        for rec in self:
            # intérêt mensuel simplifié
            rec.interest_amount = (rec.amount or 0.0) * (rec.interest_rate or 0.0) / 100.0 / 12.0
            rec.net_amount = (rec.amount or 0.0) + rec.interest_amount

    @api.constrains("company_id", "target_company_id")
    def _check_companies(self):
        for rec in self:
            if rec.company_id == rec.target_company_id:
                raise UserError(_("La société source et la société cible doivent être différentes."))

    def action_compute(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("cash.pooling.transfer") or "POOL"
            rec.state = "computed"
            rec.notes = (rec.notes or "") + ("\n[%s] %s" % (fields.Datetime.now(), _("Virement d'alignement calculé: %.2f, intérêts %.2f") % (rec.amount, rec.interest_amount)))

    def action_post(self):
        self.write({"state": "posted"})
    def action_cancel(self):
        self.write({"state": "cancelled"})
