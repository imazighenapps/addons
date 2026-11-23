# -*- coding: utf-8 -*-
import base64, json
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MassUpdateWizard(models.Model):
    _name = "mass.update.wizard"
    _description = "Mise à Jour Massive Assistée"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False, tracking=True)
    active = fields.Boolean(string="Actif", default=True)
    company_id = fields.Many2one("res.company", string="Société", required=True, default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Partenaire", tracking=True)
    user_id = fields.Many2one("res.users", string="Responsable", default=lambda self: self.env.user, tracking=True)
    date_start = fields.Date(string="Date de début", default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="Date de fin", tracking=True)
    amount = fields.Monetary(string="Montant", tracking=True)
    progress = fields.Integer(string="Progression (%)", default=0)
    priority = fields.Selection([("0","Normal"),("1","Faible"),("2","Élevé"),("3","Urgent")], string="Priorité", default="0")
    description = fields.Text(string="Description")
    note = fields.Text(string="Notes")
    log_note = fields.Text(string="Journal", readonly=True)
    export_file = fields.Binary(string="Fichier", readonly=True)
    export_filename = fields.Char(string="Nom du fichier", readonly=True)
    state = fields.Selection([
        ("draft","Brouillon"), ("confirmed","Confirmé"), ("in_progress","En cours"),
        ("done","Terminé"), ("cancelled","Annulé")
    ], string="Statut", default="draft", tracking=True, index=True)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError(_("La date de fin doit être postérieure à la date de début."))

    @api.constrains("progress")
    def _check_progress(self):
        for rec in self:
            if rec.progress < 0 or rec.progress > 100:
                raise ValidationError(_("La progression doit être comprise entre 0 et 100."))

    def _log(self, msg):
        for rec in self:
            stamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rec.log_note = ((rec.log_note or "") + "\n[%s] %s" % (stamp, msg)).strip()

    def action_confirm(self):
        for rec in self:
            if rec.name in (False, "Nouveau", _("Nouveau")):
                rec.name = self.env["ir.sequence"].next_by_code("mass.update.wizard") or _("Nouveau")
            rec.state = "confirmed"
            rec._log(_("Confirmé."))

    def action_start(self):
        for rec in self:
            if rec.state == "draft":
                rec.action_confirm()
            rec.state = "in_progress"
            if not rec.progress:
                rec.progress = 10
            rec._log(_("Démarré."))

    def action_done(self):
        for rec in self:
            rec.state = "done"
            rec.progress = 100
            rec._log(_("Terminé."))

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"
            rec._log(_("Annulé."))

    def action_reset_draft(self):
        for rec in self:
            rec.state = "draft"
            rec.progress = 0
            rec._log(_("Remis en brouillon."))

    def action_export(self):
        for rec in self:
            if rec.name in (False, "Nouveau", _("Nouveau")):
                rec.name = self.env["ir.sequence"].next_by_code("mass.update.wizard") or _("Nouveau")
            payload = {
                "module": "mass_update_wizard",
                "reference": rec.name,
                "partner": rec.partner_id.display_name if rec.partner_id else "",
                "amount": rec.amount,
                "state": rec.state,
                "progress": rec.progress,
                "date_start": str(rec.date_start or ""),
                "date_end": str(rec.date_end or ""),
                "company": rec.company_id.display_name,
            }
            data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            rec.export_filename = f"{rec.name.replace('/','_')}.json"
            rec.export_file = base64.b64encode(data).decode('ascii')
            rec._log(_("Export généré."))
