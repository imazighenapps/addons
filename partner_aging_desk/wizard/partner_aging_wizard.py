# -*- coding: utf-8 -*-
import base64
import csv
import io
from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError


class PartnerAgingWizard(models.TransientModel):
    _name = "partner.aging.wizard"
    _description = "Analyse d'ancienneté AR/AP"

    company_id = fields.Many2one(
        "res.company", string="Société", required=True, default=lambda s: s.env.company)
    as_of_date = fields.Date(string="Date d'analyse", required=True, default=fields.Date.context_today)
    aging_type = fields.Selection([
        ("receivable", "Clients (AR)"),
        ("payable", "Fournisseurs (AP)"),
    ], string="Type", required=True, default="receivable")
    partner_ids = fields.Many2many("res.partner", string="Partenaires (optionnel)")
    line_ids = fields.One2many("partner.aging.line", "wizard_id", string="Détail")
    total_0_30 = fields.Monetary(string="0-30 j", compute="_compute_totals", currency_field="currency_id")
    total_31_60 = fields.Monetary(string="31-60 j", compute="_compute_totals", currency_field="currency_id")
    total_61_90 = fields.Monetary(string="61-90 j", compute="_compute_totals", currency_field="currency_id")
    total_90p = fields.Monetary(string="> 90 j", compute="_compute_totals", currency_field="currency_id")
    total_due = fields.Monetary(string="Total dû", compute="_compute_totals", currency_field="currency_id")
    dso_dpo = fields.Float(string="DSO/DPO (jours)", compute="_compute_totals",
                           help="Délai moyen pondéré par les montants et l'ancienneté.")
    currency_id = fields.Many2one(related="company_id.currency_id")

    @api.depends("line_ids.amount_0_30", "line_ids.amount_31_60", "line_ids.amount_61_90", "line_ids.amount_90p")
    def _compute_totals(self):
        for wiz in self:
            wiz.total_0_30 = sum(wiz.line_ids.mapped("amount_0_30"))
            wiz.total_31_60 = sum(wiz.line_ids.mapped("amount_31_60"))
            wiz.total_61_90 = sum(wiz.line_ids.mapped("amount_61_90"))
            wiz.total_90p = sum(wiz.line_ids.mapped("amount_90p"))
            wiz.total_due = wiz.total_0_30 + wiz.total_31_60 + wiz.total_61_90 + wiz.total_90p
            # DSO/DPO approximatif pondéré par tranche (milieu de tranche)
            weighted = (wiz.total_0_30 * 15 + wiz.total_31_60 * 45 +
                        wiz.total_61_90 * 75 + wiz.total_90p * 120)
            wiz.dso_dpo = (weighted / wiz.total_due) if wiz.total_due else 0.0

    def _open_lines_domain(self):
        acc_type = "asset_receivable" if self.aging_type == "receivable" else "liability_payable"
        domain = [
            ("company_id", "=", self.company_id.id),
            ("account_id.account_type", "=", acc_type),
            ("parent_state", "=", "posted"),
            ("reconciled", "=", False),
            ("amount_residual", "!=", 0),
        ]
        if self.partner_ids:
            domain.append(("partner_id", "in", self.partner_ids.ids))
        return domain

    @staticmethod
    def _bucket(days):
        if days <= 30:
            return "0_30"
        if days <= 60:
            return "31_60"
        if days <= 90:
            return "61_90"
        return "90p"

    def action_compute(self):
        self.ensure_one()
        mls = self.env["account.move.line"].search(self._open_lines_domain())
        if not mls:
            raise UserError("Aucune ligne ouverte trouvée pour les critères sélectionnés.")
        self.line_ids.unlink()
        by_partner = {}
        for ml in mls:
            partner = ml.partner_id
            if not partner:
                continue
            due = ml.date_maturity or ml.date or self.as_of_date
            days = (self.as_of_date - due).days
            bucket = self._bucket(max(days, 0))
            residual = ml.amount_residual
            # pour AP on affiche en positif (dette)
            if self.aging_type == "payable":
                residual = -residual
            key = partner.id
            if key not in by_partner:
                by_partner[key] = {
                    "wizard_id": self.id,
                    "partner_id": partner.id,
                    "amount_0_30": 0.0, "amount_31_60": 0.0,
                    "amount_61_90": 0.0, "amount_90p": 0.0,
                }
            by_partner[key]["amount_%s" % bucket] += residual
        lines = []
        for vals in by_partner.values():
            total = vals["amount_0_30"] + vals["amount_31_60"] + vals["amount_61_90"] + vals["amount_90p"]
            if self.aging_type == "receivable":
                if vals["amount_90p"] > 0:
                    action = "Relance forte / mise en demeure"
                elif vals["amount_61_90"] > 0:
                    action = "Relance téléphonique"
                elif vals["amount_31_60"] > 0:
                    action = "Rappel courtois"
                else:
                    action = "Surveillance"
            else:
                if vals["amount_90p"] > 0:
                    action = "Régulariser en priorité"
                elif vals["amount_61_90"] > 0:
                    action = "Planifier paiement"
                else:
                    action = "Dans les délais"
            vals["total_due"] = total
            vals["recommended_action"] = action
            lines.append(vals)
        self.env["partner.aging.line"].create(lines)
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_export_csv(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError("Calculez d'abord l'aging.")
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        writer.writerow(["Partenaire", "0-30", "31-60", "61-90", ">90", "Total", "Action recommandée"])
        for l in self.line_ids:
            writer.writerow([l.partner_id.display_name, l.amount_0_30, l.amount_31_60,
                             l.amount_61_90, l.amount_90p, l.total_due, l.recommended_action])
        att = self.env["ir.attachment"].create({
            "name": "aging_%s_%s.csv" % (self.aging_type, self.as_of_date),
            "raw": buf.getvalue().encode("utf-8-sig"),
        })
        return {"type": "ir.actions.act_url", "url": "/web/content/%s?download=true" % att.id, "target": "self"}

    def action_print(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError("Calculez d'abord l'aging.")
        return self.env.ref("partner_aging_desk.action_report_partner_aging").report_action(self)


class PartnerAgingLine(models.TransientModel):
    _name = "partner.aging.line"
    _description = "Ligne d'aging partenaire"
    _order = "total_due desc"

    wizard_id = fields.Many2one("partner.aging.wizard", required=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Partenaire", required=True)
    currency_id = fields.Many2one(related="wizard_id.currency_id")
    amount_0_30 = fields.Monetary(string="0-30 j", currency_field="currency_id")
    amount_31_60 = fields.Monetary(string="31-60 j", currency_field="currency_id")
    amount_61_90 = fields.Monetary(string="61-90 j", currency_field="currency_id")
    amount_90p = fields.Monetary(string="> 90 j", currency_field="currency_id")
    total_due = fields.Monetary(string="Total", currency_field="currency_id")
    recommended_action = fields.Char(string="Action recommandée")
