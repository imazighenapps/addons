# -*- coding: utf-8 -*-
import re
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


class SddMandate(models.Model):
    _name = "sdd.mandate"
    _description = "Mandat de prélèvement SEPA"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, id desc"

    name = fields.Char(string="Référence mandat", required=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", string="Société", required=True, default=lambda s: s.env.company)
    partner_id = fields.Many2one("res.partner", string="Débiteur", required=True, tracking=True)
    partner_bank_id = fields.Many2one(
        "res.partner.bank", string="Compte bancaire (IBAN)", required=True,
        domain="[('partner_id', '=', partner_id)]")
    scheme = fields.Selection([
        ("CORE", "CORE"),
        ("B2B", "B2B"),
    ], string="Schéma", default="CORE", required=True)
    sequence_type = fields.Selection([
        ("FRST", "Premier (FRST)"),
        ("RCUR", "Récurrent (RCUR)"),
        ("FNAL", "Final (FNAL)"),
        ("OOFF", "Ponctuel (OOFF)"),
    ], string="Prochaine séquence", default="FRST", required=True, tracking=True)
    signature_date = fields.Date(string="Date de signature", required=True, tracking=True)
    state = fields.Selection([
        ("draft", "Brouillon"),
        ("active", "Actif"),
        ("suspended", "Suspendu"),
        ("revoked", "Révoqué"),
        ("closed", "Clôturé"),
    ], string="Statut", default="draft", tracking=True)
    last_debit_date = fields.Date(string="Dernier prélèvement", readonly=True)
    note = fields.Text(string="Notes")
    signature_attachment_id = fields.Many2one("ir.attachment", string="Mandat signé")

    _sql_constraints = [
        ("name_company_uniq", "unique(name, company_id)", "La référence de mandat doit être unique par société."),
    ]

    @api.constrains("partner_bank_id")
    def _check_iban(self):
        for m in self:
            iban = _clean_iban(getattr(m.partner_bank_id, "acc_number", False) or getattr(m.partner_bank_id, "account_number", False))
            if not _valid_iban(iban):
                raise ValidationError("IBAN invalide pour le mandat %s." % m.name)

    def action_activate(self):
        self.filtered(lambda m: m.state in ("draft", "suspended")).write({"state": "active"})

    def action_suspend(self):
        self.filtered(lambda m: m.state == "active").write({"state": "suspended"})

    def action_revoke(self):
        self.write({"state": "revoked"})

    def action_close(self):
        self.write({"state": "closed", "sequence_type": "FNAL"})

    def consume_sequence(self):
        """Appelé après génération : FRST/OOFF -> RCUR (sauf OOFF/FNAL)."""
        for m in self:
            if m.sequence_type == "FRST":
                m.sequence_type = "RCUR"
            elif m.sequence_type == "OOFF":
                m.sequence_type = "OOFF"  # ponctuel reste ponctuel si réutilisé rarement
            # RCUR reste RCUR, FNAL reste FNAL
            m.last_debit_date = fields.Date.context_today(m)
