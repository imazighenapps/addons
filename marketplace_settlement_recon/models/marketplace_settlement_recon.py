# -*- coding: utf-8 -*-
import base64, csv, io
from odoo import _, api, fields, models


class MarketplaceSettlementRecon(models.Model):
    _name = "marketplace.settlement.recon"
    _description = "Rapprochement settlement marketplace"
    _inherit = ["mail.thread"]
    _order = "settlement_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    marketplace = fields.Char(string="Marketplace", required=True)
    settlement_date = fields.Date(string="Date settlement", required=True, default=fields.Date.context_today)
    sales_amount = fields.Monetary(string="Ventes")
    commissions_amount = fields.Monetary(string="Commissions")
    ads_amount = fields.Monetary(string="Publicité / frais")
    refunds_amount = fields.Monetary(string="Remboursements")
    net_amount = fields.Monetary(string="Net encaissé", compute="_compute_net", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    export_file = fields.Binary(string="Rapport", readonly=True)
    export_filename = fields.Char(string="Nom rapport", readonly=True)
    state = fields.Selection([("draft","Brouillon"),("imported","Importé"),("reconciled","Rapproché"),("posted","Comptabilisé")], default="draft", tracking=True)
    notes = fields.Text(string="Notes")

    @api.depends("sales_amount", "commissions_amount", "ads_amount", "refunds_amount")
    def _compute_net(self):
        for rec in self:
            rec.net_amount = (rec.sales_amount or 0.0) - (rec.commissions_amount or 0.0) - (rec.ads_amount or 0.0) - (rec.refunds_amount or 0.0)

    def action_import(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("marketplace.settlement.recon") or "MKT"
            rec.state = "imported"

    def action_reconcile(self):
        for rec in self:
            buf = io.StringIO()
            w = csv.writer(buf, delimiter=';')
            w.writerow(["marketplace","date","sales","commissions","ads","refunds","net"])
            w.writerow([rec.marketplace, rec.settlement_date, rec.sales_amount, rec.commissions_amount, rec.ads_amount, rec.refunds_amount, rec.net_amount])
            rec.write({
                "export_file": base64.b64encode(buf.getvalue().encode("utf-8-sig")).decode('ascii'),
                "export_filename": f"marketplace_{rec.name.replace('/','_')}.csv",
                "state": "reconciled",
            })

    def action_post(self):
        self.write({"state": "posted"})
