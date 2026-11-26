# -*- coding: utf-8 -*-
import base64
import csv
import io
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError


def _json_dumps(data):
    return json.dumps(data, ensure_ascii=False, default=str)


class FrReportWizard(models.TransientModel):
    _name = "fr.report.wizard"
    _description = "Financial Report Wizard"

    report_id = fields.Many2one("fr.report", string="Report", required=True, ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company)
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    compare = fields.Boolean(string="Compare Period")
    compare_from = fields.Date(string="Comparison Date From")
    compare_to = fields.Date(string="Comparison Date To")
    detailed = fields.Boolean(string="Show Account Details", default=True)

    @api.onchange("compare", "date_from", "date_to")
    def _onchange_compare(self):
        for wizard in self:
            if wizard.compare and wizard.date_from and wizard.date_to and not (wizard.compare_from and wizard.compare_to):
                delta = (wizard.date_to - wizard.date_from).days
                wizard.compare_to = fields.Date.subtract(wizard.date_from, days=1)
                wizard.compare_from = fields.Date.subtract(wizard.compare_to, days=delta)

    @api.constrains("date_from", "date_to", "compare", "compare_from", "compare_to")
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError(_("The start date must be before or equal to the end date."))
            if wizard.compare:
                if not wizard.compare_from or not wizard.compare_to:
                    raise UserError(_("Set both comparison dates when comparison is enabled."))
                if wizard.compare_from > wizard.compare_to:
                    raise UserError(_("The comparison start date must be before or equal to the comparison end date."))

    def _get_move_line_domain(self, date_from, date_to):
        self.ensure_one()
        return [
            ("display_type", "not in", ("line_section", "line_note")),
            ("parent_state", "=", "posted"),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("company_id", "=", self.company_id.id),
        ]

    def _aggregate_line(self, line, date_from, date_to):
        self.ensure_one()
        aml = self.env["account.move.line"]
        domain = self._get_move_line_domain(date_from, date_to) + [("account_id", "in", self.env["account.account"].search(line._get_account_domain()).ids)]
        factor = (int(line.sign or "1")) * (-1 if line.invert else 1)
        if self.detailed:
            groups = aml._read_group(domain, groupby=["account_id"], aggregates=["debit:sum", "credit:sum"])
            detail = []
            total = 0.0
            for account, debit, credit in groups:
                balance = ((debit or 0.0) - (credit or 0.0)) * factor
                total += balance
                if account:
                    detail.append({
                        "id": account.id,
                        "code": account.code or "",
                        "name": account.name or "",
                        "amount": balance,
                    })
            detail.sort(key=lambda x: x["code"])
            return total, detail
        res = aml._read_group(domain, groupby=[], aggregates=["debit:sum", "credit:sum"])
        debit, credit = res[0] if res else (0.0, 0.0)
        return ((debit or 0.0) - (credit or 0.0)) * factor, []

    def _compute_period(self, date_from, date_to):
        self.ensure_one()
        lines = self.report_id.line_ids.sorted(key=lambda l: (l.sequence, l.id))
        by_id = {}
        for line in lines:
            if line.line_type == "line":
                amount, detail = self._aggregate_line(line, date_from, date_to)
                by_id[line.id] = {"line": line, "amount": amount, "accounts": detail}
            elif line.line_type == "title":
                by_id[line.id] = {"line": line, "amount": 0.0, "accounts": []}

        for line in lines.filtered(lambda l: l.line_type == "subtotal"):
            children = lines.filtered(lambda l: l.line_type == "line" and l.parent_id == line)
            by_id[line.id] = {
                "line": line,
                "amount": sum(by_id.get(child.id, {}).get("amount", 0.0) for child in children),
                "accounts": [],
            }

        def depth(line, cache=None):
            cache = cache or {}
            if line.id in cache:
                return cache[line.id]
            d = 0
            parent = line.parent_id
            while parent:
                d += 1
                parent = parent.parent_id
            cache[line.id] = d
            return d

        rows = []
        for line in lines:
            row = by_id.get(line.id, {"line": line, "amount": 0.0, "accounts": []})
            rows.append({
                "id": line.id,
                "code": line.code or "",
                "name": line.name,
                "line_type": line.line_type,
                "level": depth(line),
                "amount": row["amount"],
                "accounts": row.get("accounts", []),
            })
        return rows

    def _get_report_data(self):
        self.ensure_one()
        data = {
            "report": {"id": self.report_id.id, "name": self.report_id.name, "type": self.report_id.report_type},
            "company": self.company_id.name,
            "currency": self.company_id.currency_id.name,
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
        data = self._get_report_data()
        result = self.env["fr.report.result"].create({
            "report_id": self.report_id.id,
            "wizard_data": _json_dumps(data),
        })
        return {
            "type": "ir.actions.act_window",
            "name": _("Financial Report Result"),
            "res_model": "fr.report.result",
            "view_mode": "form",
            "target": "new",
            "res_id": result.id,
        }

    def action_print(self):
        self.ensure_one()
        data = self._get_report_data()
        return self.env.ref("imz_financial_reports_community.action_report_financial").report_action(self, data={"report_data": data})

    def action_export_csv(self):
        self.ensure_one()
        data = self._get_report_data()
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        header = ["Code", "Label", "Amount"]
        compare_map = {}
        if data["compare"]:
            compare_map = {r["id"]: r["amount"] for r in data["compare"]["rows"]}
            header += ["Comparison Amount", "Delta"]
        writer.writerow(header)
        for row in data["rows"]:
            label = ("  " * row["level"]) + row["name"]
            vals = [row["code"], label, "%.2f" % row["amount"]]
            if data["compare"]:
                cmp_amt = compare_map.get(row["id"], 0.0)
                vals += ["%.2f" % cmp_amt, "%.2f" % (row["amount"] - cmp_amt)]
            writer.writerow(vals)
            for acc in row.get("accounts", []):
                acc_vals = [acc["code"], ("  " * (row["level"] + 1)) + acc["name"], "%.2f" % acc["amount"]]
                if data["compare"]:
                    acc_vals += ["", ""]
                writer.writerow(acc_vals)
        csv_bytes = buf.getvalue().encode("utf-8-sig")
        att_vals = {
            "name": "%s_%s_%s.csv" % (self.report_id.report_type, self.date_from, self.date_to),
            "type": "binary",
            "mimetype": "text/csv",
        }
        if "raw" in self.env["ir.attachment"]._fields:
            att_vals["raw"] = csv_bytes
        else:
            att_vals["datas"] = base64.b64encode(csv_bytes)
        attachment = self.env["ir.attachment"].create(att_vals)
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }


class FrReportResult(models.TransientModel):
    _name = "fr.report.result"
    _description = "Financial Report Result"

    report_id = fields.Many2one("fr.report", string="Report", readonly=True)
    wizard_data = fields.Text(string="Data", readonly=True)
    html_preview = fields.Html(string="Preview", compute="_compute_html_preview", sanitize=False)

    @api.depends("wizard_data")
    def _compute_html_preview(self):
        for rec in self:
            if not rec.wizard_data:
                rec.html_preview = False
                continue
            data = json.loads(rec.wizard_data)
            compare = bool(data.get("compare"))
            headers = "<th>Code</th><th>Label</th><th style='text-align:right'>Amount</th>"
            if compare:
                headers += "<th style='text-align:right'>Comparison</th><th style='text-align:right'>Delta</th>"
            parts = [
                "<div>",
                "<h3>%s - %s</h3>" % (data["report"]["name"], data["company"]),
                "<p>%s to %s (%s)</p>" % (data["period_from"], data["period_to"], data.get("currency", "")),
                "<table class='table table-sm table-striped'><thead><tr>%s</tr></thead><tbody>" % headers,
            ]
            cmp_map = {r["id"]: r["amount"] for r in data["compare"]["rows"]} if compare else {}
            for row in data["rows"]:
                style = "padding-left:%dpx;" % (row["level"] * 20)
                if row["line_type"] == "title":
                    style += "font-weight:700;"
                if row["line_type"] == "subtotal":
                    style += "font-weight:700;border-top:1px solid #999;"
                amount = row["amount"]
                row_html = "<tr><td>%s</td><td style='%s'>%s</td><td style='text-align:right'>%.2f</td>" % (
                    row["code"], style, row["name"], amount)
                if compare:
                    cmp_amt = cmp_map.get(row["id"], 0.0)
                    row_html += "<td style='text-align:right'>%.2f</td><td style='text-align:right'>%.2f</td>" % (cmp_amt, amount - cmp_amt)
                row_html += "</tr>"
                parts.append(row_html)
                for acc in row.get("accounts", []):
                    acc_style = "padding-left:%dpx;color:#555;" % ((row["level"] + 1) * 20)
                    acc_row = "<tr><td>%s</td><td style='%s'>%s</td><td style='text-align:right'>%.2f</td>" % (
                        acc["code"], acc_style, acc["name"], acc["amount"])
                    if compare:
                        acc_row += "<td></td><td></td>"
                    acc_row += "</tr>"
                    parts.append(acc_row)
            parts.append("</tbody></table></div>")
            rec.html_preview = "".join(parts)
