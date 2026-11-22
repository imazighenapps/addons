# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class RateProviderSync(models.Model):
    _name = "rate.provider.sync"
    _description = "Synchronisation des taux de change"
    _inherit = ["mail.thread"]
    _order = "sync_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", string="Devise", required=True)
    provider = fields.Selection([("ecb","BCE/ECB"),("manual","Manuel")], default="ecb", required=True)
    sync_date = fields.Date(string="Date de synchronisation", default=fields.Date.context_today)
    rate = fields.Float(string="Taux", required=True, digits=(12,6))
    previous_rate = fields.Float(string="Taux précédent", digits=(12,6))
    variation_pct = fields.Float(string="Variation (%)", compute="_compute_variation", store=True)
    alert = fields.Boolean(string="Alerte écart anormal", compute="_compute_variation", store=True)
    alert_threshold = fields.Float(string="Seuil alerte (%)", default=5.0)
    state = fields.Selection([("draft","Brouillon"),("synced","Synchronisé"),("manual","Saisi manuellement")], default="draft", tracking=True)
    justification = fields.Text(string="Justification (si manuel)")
    notes = fields.Text(string="Journal de synchronisation")

    @api.depends("rate", "previous_rate", "alert_threshold")
    def _compute_variation(self):
        for rec in self:
            if rec.previous_rate:
                rec.variation_pct = abs(rec.rate - rec.previous_rate) / rec.previous_rate * 100.0
            else:
                rec.variation_pct = 0.0
            rec.alert = rec.variation_pct > (rec.alert_threshold or 0.0) and rec.previous_rate > 0

    def action_sync(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("rate.provider.sync") or "RATE"
            rec.state = "synced" if rec.provider != "manual" else "manual"
            rec.notes = (rec.notes or "") + ("\n[%s] %s %s = %s" % (fields.Datetime.now(), rec.currency_id.name, rec.sync_date, rec.rate))
