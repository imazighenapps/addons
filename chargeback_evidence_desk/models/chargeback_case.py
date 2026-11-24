# -*- coding: utf-8 -*-
import base64, json
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ChargebackCase(models.Model):
    _name = "chargeback.case"
    _description = "Dossier de contestation (chargeback)"
    _inherit = ["mail.thread"]
    _order = "deadline_date asc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one("account.move", string="Facture", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),('company_id','=',company_id),('state','=','posted')]")
    sale_order_id = fields.Many2one("sale.order", string="Commande")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    amount = fields.Monetary(string="Montant contesté", required=True)
    currency_id = fields.Many2one(related="invoice_id.currency_id", store=True, readonly=True)
    processor = fields.Char(string="Processeur de paiement")
    reason = fields.Char(string="Motif")
    opened_date = fields.Date(string="Date d'ouverture", default=fields.Date.context_today)
    deadline_date = fields.Date(string="Date limite de réponse")
    evidence_file = fields.Binary(string="Dossier de preuve", readonly=True)
    evidence_filename = fields.Char(string="Nom du fichier", readonly=True)
    evidence_summary = fields.Text(string="Résumé des preuves", readonly=True)
    outcome = fields.Selection([("pending","En cours"),("won","Gagné"),("lost","Perdu")], default="pending", tracking=True)
    state = fields.Selection([("draft","Brouillon"),("assembled","Dossier assemblé"),("submitted","Soumis"),("closed","Clos")], default="draft", tracking=True)
    notes = fields.Text(string="Notes")

    def action_assemble(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("chargeback.case") or "CBK"
            evidence = {
                "case": rec.name, "invoice": rec.invoice_id.name, "partner": rec.partner_id.name,
                "amount": rec.amount, "currency": rec.currency_id.name,
                "sale_order": rec.sale_order_id.name or "",
                "opened": str(rec.opened_date or ""), "deadline": str(rec.deadline_date or ""),
                "reason": rec.reason or "", "company": rec.company_id.name,
                "items": [{"name": l.name, "qty": l.quantity, "subtotal": l.price_subtotal} for l in rec.invoice_id.invoice_line_ids],
            }
            content = json.dumps(evidence, indent=2, ensure_ascii=False).encode("utf-8")
            rec.write({
                "evidence_file": base64.b64encode(content).decode("ascii"),
                "evidence_filename": "%s_evidence.json" % rec.name.replace("/", "_"),
                "evidence_summary": _("Preuves assemblées: facture, lignes, commande, dates, motif."),
                "state": "assembled",
            })

    def action_submit(self):
        if not self.evidence_file:
            raise UserError(_("Assemblez d'abord le dossier de preuve."))
        self.state = "submitted"

    def action_close(self):
        self.write({"state": "closed"})
