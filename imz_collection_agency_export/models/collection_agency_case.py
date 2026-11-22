# -*- coding: utf-8 -*-
import base64, csv, io
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CollectionAgencyCase(models.Model):
    _name = "collection.agency.case"
    _description = "Transmission agence de recouvrement"
    _inherit = ["mail.thread"]
    _order = "transfer_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    agency_name = fields.Char(string="Agence", required=True)
    invoice_id = fields.Many2one("account.move", string="Facture impayée", required=True,
        domain="[('move_type','=','out_invoice'),('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    amount_due = fields.Monetary(string="Montant dû", required=True)
    commission_rate = fields.Float(string="Commission agence (%)", default=15.0)
    commission_amount = fields.Monetary(string="Commission", compute="_compute_commission", store=True)
    recovered_amount = fields.Monetary(string="Montant récupéré", default=0.0)
    remitted_amount = fields.Monetary(string="Versement net", compute="_compute_commission", store=True)
    transfer_date = fields.Date(string="Date de transmission", default=fields.Date.context_today)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    export_file = fields.Binary(string="Dossier d'envoi", readonly=True)
    export_filename = fields.Char(string="Nom fichier", readonly=True)
    state = fields.Selection([("draft","Brouillon"),("sent","Transmis"),("partial","Récupération partielle"),("recovered","Récupéré"),("closed","Clos")], default="draft", tracking=True)
    notes = fields.Text(string="Notes")

    @api.depends("amount_due", "commission_rate", "recovered_amount")
    def _compute_commission(self):
        for rec in self:
            rec.commission_amount = (rec.recovered_amount or 0.0) * (rec.commission_rate or 0.0) / 100.0
            rec.remitted_amount = (rec.recovered_amount or 0.0) - rec.commission_amount

    def action_send(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("collection.agency.case") or "COLL"
            buf = io.StringIO()
            w = csv.writer(buf, delimiter=';')
            w.writerow(["reference","agency","invoice","partner","amount_due","commission_rate"])
            w.writerow([rec.name, rec.agency_name, rec.invoice_id.name or "", rec.partner_id.name or "", rec.amount_due, rec.commission_rate])
            rec.write({
                "export_file": base64.b64encode(buf.getvalue().encode("utf-8-sig")).decode('ascii'),
                "export_filename": "%s_dossier.csv" % rec.name.replace("/", "_"),
                "state": "sent",
            })

    def action_register_recovery(self):
        for rec in self:
            if (rec.recovered_amount or 0.0) >= (rec.amount_due or 0.0):
                rec.state = "recovered"
            elif (rec.recovered_amount or 0.0) > 0:
                rec.state = "partial"
            else:
                raise UserError(_("Saisissez un montant récupéré."))

    def action_close(self):
        self.write({"state": "closed"})
