# -*- coding: utf-8 -*-
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


def _clean_iban(iban):
    return (iban or "").replace(" ", "").upper()


def _valid_iban(iban):
    iban = _clean_iban(iban)
    if not re.match(r"^[A-Z]{2}[0-9A-Z]{13,32}$", iban):
        return False
    rearranged = iban[4:] + iban[:4]
    num = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    try:
        return int(num) % 97 == 1
    except Exception:
        return False


class MandateLifecycle(models.Model):
    _name = "mandate.lifecycle"
    _description = "Mandat SEPA - Cycle de vie"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, id desc"

    name = fields.Char(string="Référence mandat", required=True, copy=False, tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Société", required=True, default=lambda s: s.env.company)
    partner_id = fields.Many2one("res.partner", string="Partenaire", required=True, tracking=True)
    iban = fields.Char(string="IBAN actuel", required=True, tracking=True)
    bic = fields.Char(string="BIC", tracking=True)
    state = fields.Selection([
        ("new", "Nouveau"),
        ("active", "Actif"),
        ("suspended", "Suspendu"),
        ("revoked", "Révoqué"),
        ("expired", "Expiré"),
    ], string="Statut", default="new", tracking=True, required=True)
    signature_date = fields.Date(string="Date de signature", tracking=True)
    activation_date = fields.Date(string="Date d'activation", tracking=True)
    revocation_date = fields.Date(string="Date de révocation", tracking=True)
    expiry_date = fields.Date(string="Date d'expiration", tracking=True,
                              help="Date limite de validité du mandat (si applicable).")
    signed_document_ids = fields.Many2many(
        "ir.attachment", "mandate_lifecycle_attachment_rel", "mandate_id", "attachment_id",
        string="Pièces signées")
    rib_history_ids = fields.One2many("mandate.lifecycle.rib", "mandate_id", string="Historique RIB")
    alert_expiring = fields.Boolean(string="Alerte expiration", compute="_compute_alerts", store=True)
    alert_revoked = fields.Boolean(string="Alerte révocation", compute="_compute_alerts", store=True)
    note = fields.Text(string="Notes")

    _sql_constraints = [
        ("name_company_uniq", "unique(name, company_id)", "Référence de mandat unique par société."),
    ]

    @api.constrains("iban")
    def _check_iban(self):
        for m in self:
            if not _valid_iban(m.iban):
                raise ValidationError("IBAN invalide pour le mandat %s." % m.name)

    @api.depends("state", "expiry_date", "revocation_date")
    def _compute_alerts(self):
        today = fields.Date.context_today(self)
        soon = today + timedelta(days=30)
        for m in self:
            m.alert_revoked = m.state == "revoked"
            m.alert_expiring = bool(
                m.expiry_date and m.state == "active" and today <= m.expiry_date <= soon)

    def action_activate(self):
        for m in self:
            m.write({"state": "active", "activation_date": fields.Date.context_today(m)})

    def action_suspend(self):
        self.filtered(lambda m: m.state == "active").write({"state": "suspended"})

    def action_revoke(self):
        self.write({"state": "revoked", "revocation_date": fields.Date.context_today(self)})

    def action_set_new(self):
        self.write({"state": "new"})

    def action_change_rib(self, new_iban, new_bic=False, reason=False):
        """Enregistre un changement de RIB en historisant l'ancien."""
        for m in self:
            self.env["mandate.lifecycle.rib"].create({
                "mandate_id": m.id,
                "old_iban": m.iban,
                "old_bic": m.bic,
                "new_iban": _clean_iban(new_iban),
                "new_bic": (new_bic or "").upper() or False,
                "change_date": fields.Date.context_today(m),
                "reason": reason,
            })
            m.write({"iban": _clean_iban(new_iban), "bic": (new_bic or "").upper() or False})

    @api.model
    def _cron_check_expiry(self):
        today = fields.Date.context_today(self)
        expired = self.search([
            ("state", "=", "active"),
            ("expiry_date", "!=", False),
            ("expiry_date", "<", today),
        ])
        expired.write({"state": "expired"})
        return True


class MandateLifecycleRib(models.Model):
    _name = "mandate.lifecycle.rib"
    _description = "Historique RIB de mandat"
    _order = "change_date desc, id desc"

    mandate_id = fields.Many2one("mandate.lifecycle", required=True, ondelete="cascade")
    change_date = fields.Date(string="Date de changement", required=True, default=fields.Date.context_today)
    old_iban = fields.Char(string="Ancien IBAN")
    old_bic = fields.Char(string="Ancien BIC")
    new_iban = fields.Char(string="Nouvel IBAN", required=True)
    new_bic = fields.Char(string="Nouveau BIC")
    reason = fields.Char(string="Motif")

    @api.constrains("new_iban")
    def _check_new_iban(self):
        for r in self:
            if not _valid_iban(r.new_iban):
                raise ValidationError("Nouvel IBAN invalide.")
