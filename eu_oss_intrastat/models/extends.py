# -*- coding: utf-8 -*-
import base64
import csv
import io

from odoo import api, fields, models


class IntrastatExport(models.TransientModel):
    _name = "intrastat.export"
    _description = "Intrastat Declaration Export"

    period = fields.Char(default=lambda self: fields.Date.today().strftime("%Y-%m"))
    direction = fields.Selection(
        [("dispatch", "Dispatch"), ("arrival", "Arrival")],
        default="dispatch", required=True)
    only_ready = fields.Boolean(string="Only Ready Lines", default=True)
    line_ids = fields.Many2many("intrastat.line", string="Lines")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Exported")], default="draft")
    filename = fields.Char(readonly=True)
    file_data = fields.Binary(readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        domain = [("period", "=", res.get("period",
                                          fields.Date.today().strftime("%Y-%m")))]
        if res.get("direction"):
            domain.append(("direction", "=", res["direction"]))
        if res.get("only_ready", True):
            domain.append(("state", "in", ("ready", "declared")))
        res["line_ids"] = [(6, 0, self.env["intrastat.line"].search(domain).ids)]
        return res

    def action_export(self):
        self.ensure_one()
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        writer.writerow(["period", "direction", "flow_code", "country",
                         "partner", "commodity", "amount_untaxed"])
        for line in self.line_ids:
            writer.writerow([
                line.period,
                line.direction,
                "D" if line.direction == "dispatch" else "A",
                line.country_code or "",
                line.partner_code or "",
                line.product_code or "",
                round(line.amount or 0.0, 2),
            ])
        payload = buf.getvalue().encode("utf-8")
        filename = "intrastat_%s_%s.csv" % (self.direction, self.period)
        self.write({
            "filename": filename,
            "file_data": base64.b64encode(payload),
            "state": "done",
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % self.id,
            "target": "self",
        }