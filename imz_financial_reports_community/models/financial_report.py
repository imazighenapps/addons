# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models
from odoo.exceptions import UserError

REPORT_TYPES = [
    ("pl", "Compte de résultat"),
    ("bs", "Bilan"),
    ("cashflow", "Trésorerie"),
    ("balance", "Balance des comptes"),
    ("custom", "Personnalisé"),
]

LINE_TYPES = [
    ("title", "Titre de section"),
    ("line", "Ligne de comptes"),
    ("subtotal", "Sous-total des sous-lignes"),
]


class FrReport(models.Model):
    """Définition d'un état financier (compte de résultat, bilan, ...)."""
    _name = "fr.report"
    _description = "État financier (Community)"
    _order = "sequence, id"

    name = fields.Char(string="Nom de l'état", required=True, translate=True)
    sequence = fields.Integer(default=10)
    report_type = fields.Selection(REPORT_TYPES, string="Type", required=True,
                                   default="custom")
    active = fields.Boolean(default=True)
    line_ids = fields.One2many("fr.report.line", "report_id", string="Lignes",
                               copy=True)
    company_id = fields.Many2one("res.company", string="Société",
                                 default=lambda s: s.env.company)
    note = fields.Text(string="Notes")

    def action_open_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "fr.report.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_report_id": self.id,
                "default_date_from": fields.Date.context_today(self).replace(month=1, day=1),
                "default_date_to": fields.Date.context_today(self),
            },
        }


class FrReportLine(models.Model):
    """Ligne d'un état : titre, agrégat de comptes ou sous-total."""
    _name = "fr.report.line"
    _description = "Ligne d'état financier"
    _order = "sequence, id"

    report_id = fields.Many2one("fr.report", string="État", required=True,
                                ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    code = fields.Char(string="Code")
    name = fields.Char(string="Libellé", required=True, translate=True)
    line_type = fields.Selection(LINE_TYPES, string="Type de ligne", default="line",
                                 required=True)
    parent_id = fields.Many2one("fr.report.line", string="Section parente",
                                domain="[('id', '!=', id), ('report_id', '=', report_id),"
                                       " ('line_type', 'in', ('title', 'subtotal'))]",
                                ondelete="restrict")
    sign = fields.Selection([("1", "Crédit - Débit"), ("-1", "Débit - Crédit")],
                            string="Sens", default="1", required=True)
    internal_group = fields.Selection(
        [("equity", "Capitaux propres"), ("asset", "Actif"),
         ("liability", "Passif"), ("income", "Produits"),
         ("expense", "Charges"), ("off", "Hors bilan")],
        string="Groupe interne",
        help="Agrège tous les comptes de ce groupe interne (natif Odoo 20).")
    account_ids = fields.Many2many(
        "account.account", string="Comptes explicitement listés")
    code_prefixes = fields.Char(
        string="Préfixes de comptes",
        help="Liste de préfixes séparés par des virgules, ex. : 7,706,641.")
    invert = fields.Boolean(
        string="Inverser le sens",
        help="Inverse le sens de la ligne pour un usage spécifique (ex. : "
             "présentation actif/passif).")

    @api.constrains("code_prefixes")
    def _check_code_prefixes(self):
        for line in self:
            if not line.code_prefixes:
                continue
            for part in line.code_prefixes.split(","):
                if part.strip() and not part.strip().replace(".", "").isdigit():
                    raise UserError(
                        "Préfixe invalide « %s » : attendu une suite de chiffres." % part)

    @api.constrains("line_type", "internal_group", "account_ids", "code_prefixes")
    def _check_line_has_accounts(self):
        for line in self:
            if line.line_type == "line" and not (
                    line.internal_group or line.account_ids or line.code_prefixes):
                raise UserError(
                    "La ligne « %s » doit référencer des comptes : groupe interne, "
                    "comptes ou préfixes." % line.name)
            if line.line_type == "line" and (
                    line.internal_group and (line.account_ids or line.code_prefixes)):
                raise UserError(
                    "La ligne « %s » doit utiliser UNE source de comptes "
                    "(groupe interne OU comptes OU préfixes)." % line.name)

    def _account_domain(self):
        """Domaine account.account correspondant à la source de la ligne."""
        self.ensure_one()
        if self.internal_group:
            return [("internal_group", "=", self.internal_group)]
        if self.account_ids:
            return [("id", "in", self.account_ids.ids)]
        if self.code_prefixes:
            prefixes = [p.strip() for p in self.code_prefixes.split(",") if p.strip()]
            if not prefixes:
                return [("id", "=", 0)]
            domain = ["|"] * (len(prefixes) - 1)
            for p in prefixes:
                domain += [("code", "=like", p + "%")]
            return domain
        return [("id", "=", 0)]


class FrReportWizard(models.TransientModel):
    """Exécution d'un état sur une période, avec période de comparaison optionnelle."""
    _name = "fr.report.wizard"
    _description = "Exécuter un état financier"

    report_id = fields.Many2one("fr.report", string="État", required=True,
                                ondelete="cascade")
    company_id = fields.Many2one("res.company", string="Société", required=True,
                                 default=lambda s: s.env.company)
    date_from = fields.Date(string="Du", required=True)
    date_to = fields.Date(string="Au", required=True)
    compare = fields.Boolean(string="Comparer une période")
    compare_from = fields.Date(string="Comparaison du")
    compare_to = fields.Date(string="Comparaison au")
    detailed = fields.Boolean(string="Détail par compte", default=True)
    export_csv = fields.Boolean(string="Exporter en CSV")

    @api.onchange("compare")
    def _onchange_compare(self):
        """Pré-remplit la comparaison avec la période précédente de même durée."""
        for wiz in self:
            if wiz.compare and wiz.date_from and wiz.date_to and not (
                    wiz.compare_from and wiz.compare_to):
                from datetime import timedelta
                length = (wiz.date_to - wiz.date_from).days + 1
                wiz.compare_to = wiz.date_from - timedelta(days=1)
                wiz.compare_from = wiz.compare_to - timedelta(days=length - 1)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for wiz in self:
            if wiz.date_from > wiz.date_to:
                raise UserError("La date « Du » doit précéder la date « Au ».")
            if wiz.compare and (not wiz.compare_from or not wiz.compare_to):
                raise UserError(
                    "Renseignez les bornes de la période de comparaison.")
            if wiz.compare and wiz.compare_from > wiz.compare_to:
                raise UserError("La comparaison « Du » doit précéder « Au ».")

    def _aml_domain(self, date_from, date_to):
        self.ensure_one()
        return [
            ("display_type", "not in", ("line_section", "line_note")),
            ("move_id.state", "=", "posted"),
            ("move_id.date", ">=", date_from),
            ("move_id.date", "<=", date_to),
            ("company_id", "=", self.company_id.id),
        ]

    def _aggregate_line(self, line, date_from, date_to, by_account=False):
        """Solde signé d'une ligne (et le détail par compte si demandé).

        Odoo 20 : _read_group renvoie des tuples (valeurs groupby, puis agrégats).
        """
        aml = self.env["account.move.line"]
        accounts = self.env["account.account"].search(line._account_domain())
        if not accounts:
            return 0.0, {}
        domain = self._aml_domain(date_from, date_to) + [
            ("account_id", "in", accounts.ids)]
        factor = (int(line.sign or 1) or 1) * (-1 if line.invert else 1)
        if by_account:
            rows = aml._read_group(
                domain, groupby=["account_id"],
                aggregates=["debit:sum", "credit:sum"])
            detail = {}
            total = 0.0
            for account, debit, credit in rows:
                balance = (debit or 0.0) - (credit or 0.0)
                total += balance
                detail[account[0]] = balance
            total *= factor
            detail = {k: v * factor for k, v in detail.items()}
            return total, detail
        debit, credit = aml._read_group(
            domain, groupby=[], aggregates=["debit:sum", "credit:sum"])[0]
        return ((debit or 0.0) - (credit or 0.0)) * factor, {}

    def _compute_period(self, date_from, date_to):
        report = self.report_id
        rows = []
        lines = report.line_ids
        by_id = {l.id: None for l in lines}
        for line in lines:
            if line.line_type == "line":
                total, detail = self._aggregate_line(
                    line, date_from, date_to, by_account=self.detailed)
                accounts = []
                if self.detailed and detail:
                    accs = self.env["account.account"].browse(detail.keys())
                    accounts = [
                        {"code": a.code, "name": a.name, "amount": detail[a.id]}
                        for a in sorted(accs, key=lambda x: x.code)]
                by_id[line.id] = {"line": line, "amount": total,
                                  "accounts": accounts, "level": 0}
        for line in lines:
            if line.line_type == "subtotal":
                amount = 0.0
                for child in lines.filtered(
                        lambda l: l.line_type == "line" and l.parent_id.id == line.id):
                    amount += by_id[child.id]["amount"]
                by_id[line.id] = {"line": line, "amount": amount,
                                  "accounts": [], "level": 0}
        for line in lines:
            if line.line_type == "title":
                by_id[line.id] = {"line": line, "amount": 0.0,
                                  "accounts": [], "level": 0}
        level_cache = {}

        def depth(l):
            if l.id in level_cache:
                return level_cache[l.id]
            d = 0
            p = l.parent_id
            while p:
                d += 1
                p = p.parent_id
            level_cache[l.id] = d
            return d

        for line in lines:
            row = by_id[line.id]
            row["level"] = depth(line)
            rows.append(row)
        return rows

    def _execute(self):
        self.ensure_one()
        data = {
            "report": self.report_id.read(["name", "report_type"])[0],
            "company": self.company_id.name,
            "period_from": self.date_from.isoformat(),
            "period_to": self.date_to.isoformat(),
            "rows": self._compute_period(self.date_from, self.date_to),
            "compare": None,
        }
        if self.compare:
            data["compare"] = {
                "period_from": self.compare_from.isoformat(),
                "period_to": self.compare_to.isoformat(),
                "rows": self._compute_period(self.compare_from, self.compare_to),
            }
        return data

    def action_view(self):
        self.ensure_one()
        data = self._execute()
        action = {
            "type": "ir.actions.act_window",
            "res_model": "fr.report.result",
            "view_mode": "form",
            "target": "new",
        }
        result = self.env["fr.report.result"].create({
            "wizard_data": json_dumps(data),
            "report_id": self.report_id.id,
        })
        action["res_id"] = result.id
        return action

    def action_print(self):
        self.ensure_one()
        data = self._execute()
        return self.env.ref(
            "imz_financial_reports_community.action_report_financial"
        ).report_action(self, data={"report_data": data})

    def action_export_csv(self):
        self.ensure_one()
        import csv as _csv
        import io as _io
        import base64 as _b64
        buf = _io.StringIO()
        writer = _csv.writer(buf, delimiter=";")
        writer.writerow(["Code", "Libellé", "Montant"])
        data = self._execute()
        rows = data["rows"]
        compare = {r["line"]["id"]: r["amount"] for r in data["compare"]["rows"]} \
            if data["compare"] else {}
        for row in rows:
            line = row["line"]
            amt = row["amount"]
            delta = ""
            if compare and line["id"] in compare:
                delta = "%.2f" % (amt - compare[line["id"]])
            writer.writerow([line["code"] or "", "  " * row["level"] + line["name"],
                             "%.2f" % amt, delta])
            for acc in row.get("accounts", []):
                writer.writerow([acc["code"], "     " + acc["name"],
                                 "%.2f" % acc["amount"], ""])
        attachment = self.env["ir.attachment"].create({
            "name": "%s_%s_%s.csv" % (
                self.report_id.report_type,
                self.date_from.isoformat(), self.date_to.isoformat()),
            "raw": buf.getvalue().encode("utf-8-sig"),
            "type": "binary",
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }


def json_dumps(data):
    return json.dumps(data, ensure_ascii=False, default=str)


class FrReportResult(models.TransientModel):
    """Porteur d'affichage du résultat (formulaire de synthèse)."""
    _name = "fr.report.result"
    _description = "Résultat d'état financier"

    report_id = fields.Many2one("fr.report", string="État")
    wizard_data = fields.Text(string="Données")
    html = fields.Html(string="Aperçu", compute="_compute_html")

    @api.depends("wizard_data")
    def _compute_html(self):
        for rec in self:
            if not rec.wizard_data:
                rec.html = False
                continue
            data = json.loads(rec.wizard_data)
            parts = ["<h3>%s — %s (%s → %s)</h3>" % (
                data["report"]["name"], data["company"],
                data["period_from"], data["period_to"])]
            parts.append("<table class='table'><tr><th>Libellé</th>"
                         "<th style='text-align:right'>Montant</th></tr>")
            for row in data["rows"]:
                style = ""
                if row["line"]["line_type"] == "title":
                    style = "font-weight:bold;"
                if row["line"]["line_type"] == "subtotal":
                    style = "font-weight:bold;border-top:1px solid;"
                parts.append("<tr><td style='padding-left:%spx;%s'>%s</td>"
                             "<td style='text-align:right;%s'>%.2f</td></tr>" % (
                                 row["level"] * 24, style, row["line"]["name"],
                                 style, row["amount"]))
            parts.append("</table>")
            rec.html = "".join(parts)
