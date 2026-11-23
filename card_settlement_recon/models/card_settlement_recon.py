# -*- coding: utf-8 -*-
import base64, csv, io
from odoo import _, api, fields, models


class CardSettlementRecon(models.Model):
    _name = "card.settlement.recon"
    _description = "Rapprochement settlement cartes/PSP"
    _inherit = ["mail.thread"]
    _order = "settlement_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    provider = fields.Char(string="PSP / Fournisseur", required=True)
    settlement_date = fields.Date(string="Date settlement", required=True, default=fields.Date.context_today)
    gross_amount = fields.Monetary(string="Montant brut")
    fees_amount = fields.Monetary(string="Commissions")
    refunds_amount = fields.Monetary(string="Remboursements")
    net_amount = fields.Monetary(string="Net encaissé", compute="_compute_net", store=True)
    transactions_count = fields.Integer(string="Nombre de transactions")
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    import_file = fields.Binary(string="Fichier settlement")
    import_filename = fields.Char(string="Nom fichier import")
    export_file = fields.Binary(string="Rapport")
    export_filename = fields.Char(string="Nom rapport")
    state = fields.Selection([("draft","Brouillon"),("imported","Importé"),("reconciled","Rapproché"),("posted","Comptabilisé")], default="draft", tracking=True)
    notes = fields.Text(string="Notes")

    @api.depends("gross_amount", "fees_amount", "refunds_amount")
    def _compute_net(self):
        for rec in self:
            rec.net_amount = (rec.gross_amount or 0.0) - (rec.fees_amount or 0.0) - (rec.refunds_amount or 0.0)

    def action_import(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("card.settlement.recon") or "PSP"
            rec.state = "imported"

    def action_reconcile(self):
        for rec in self:
            buf = io.StringIO()
            w = csv.writer(buf, delimiter=';')
            w.writerow(["provider","date","gross","fees","refunds","net","transactions"])
            w.writerow([rec.provider, rec.settlement_date, rec.gross_amount, rec.fees_amount, rec.refunds_amount, rec.net_amount, rec.transactions_count])
            rec.write({
                "export_file": base64.b64encode(buf.getvalue().encode("utf-8-sig")).decode('ascii'),
                "export_filename": f"settlement_{rec.name.replace('/','_')}.csv",
                "state": "reconciled",
            })

    def action_post(self):
        self.write({"state": "posted"})
