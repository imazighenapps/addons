# -*- coding: utf-8 -*-
import base64
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError

PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")


class ReportForgeTemplate(models.Model):
    _name = "report.forge.template"
    _description = "Document Template"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    model_name = fields.Selection(
        [("res.partner", "Contact"),
         ("sale.order", "Quotation / Order"),
         ("account.move", "Invoice / Credit Note"),
         ("product.template", "Product")],
        string="Applies To", required=True, default="res.partner")
    body_html = fields.Html(
        string="Body", required=True,
        help="Use {{ field_name }} or {{ partner_id.name }}. "
             "Use {{ lines }} to insert the document lines table.")
    header_html = fields.Html(string="Header")
    footer_html = fields.Html(string="Footer")
    active = fields.Boolean(default=True)
    version = fields.Integer(default=1)
    note = fields.Text()

    def _value(self, record, path):
        value = record
        for part in path.split("."):
            if not value:
                return ""
            if isinstance(value, models.BaseModel):
                if part not in value._fields:
                    return ""
                value = value[part]
            else:
                value = getattr(value, part, "")
        if value is False or value is None:
            return ""
        if isinstance(value, bool):
            return _("Yes") if value else _("No")
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        if isinstance(value, float):
            return "{:,.2f}".format(value)
        return str(value)

    def _lines_table(self, record):
        if "order_line" in record._fields:
            lines = record.order_line
        elif "invoice_line_ids" in record._fields:
            lines = record.invoice_line_ids
        else:
            return ""
        if not lines:
            return ""
        rows = []
        for line in lines:
            label = line.product_id.display_name if "product_id" in line._fields \
                else (line.name or line.display_name)
            qty = line.quantity if "quantity" in line._fields \
                else line.product_uom_qty
            rows.append(
                "<tr><td>" + label + "</td>"
                "<td style='text-align:right'>" + str(qty) + "</td>"
                "<td style='text-align:right'>"
                + "{:,.2f}".format(line.price_unit) + "</td>"
                "<td style='text-align:right'>"
                + "{:,.2f}".format(line.price_subtotal) + "</td></tr>")
        return (
            "<table class='table table-sm' "
            "style='width:100%;border-collapse:collapse'>"
            "<thead><tr><th style='text-align:left'>Description</th>"
            "<th style='text-align:right'>Qty</th>"
            "<th style='text-align:right'>Unit Price</th>"
            "<th style='text-align:right'>Subtotal</th></tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody></table>")

    def render(self, record):
        self.ensure_one()
        body = self.body_html or ""
        body = body.replace("{{ lines }}", self._lines_table(record))
        body = body.replace("{{lines}}", self._lines_table(record))
        body = PLACEHOLDER.sub(
            lambda match: self._value(record, match.group(1)), body)
        header = self.header_html or ""
        footer = self.footer_html or ""
        header = PLACEHOLDER.sub(
            lambda match: self._value(record, match.group(1)), header)
        footer = PLACEHOLDER.sub(
            lambda match: self._value(record, match.group(1)), footer)
        return header, body, footer

    def action_duplicate(self):
        self.ensure_one()
        copy = self.copy({"name": _("%s (copy)") % self.name})
        return {
            "type": "ir.actions.act_window",
            "res_model": "report.forge.template",
            "res_id": copy.id,
            "view_mode": "form",
            "target": "current",
        }


class ReportForgeDocument(models.Model):
    _name = "report.forge.document"
    _description = "Generated Document"
    _inherit = ["mail.thread"]
    _order = "generated_on desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    template_id = fields.Many2one(
        "report.forge.template", string="Template", required=True,
        ondelete="restrict")
    template_version = fields.Integer(readonly=True)
    res_model = fields.Char(string="Model", required=True)
    res_id = fields.Integer(string="Record ID", required=True)
    record_name = fields.Char(string="Record")
    rendered_html = fields.Html(readonly=True)
    attachment_id = fields.Many2one("ir.attachment", string="PDF")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Generated")], default="draft")
    generated_on = fields.Datetime(default=fields.Datetime.now, readonly=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "report.forge.document") or "/"
            if vals.get("template_id") and not vals.get("template_version"):
                template = self.env["report.forge.template"].browse(
                    vals["template_id"])
                vals["template_version"] = template.version
        return super().create(vals_list)

    def _get_record(self):
        self.ensure_one()
        if self.res_model not in self.env:
            raise UserError(_("Unknown model %s.") % self.res_model)
        record = self.env[self.res_model].browse(self.res_id)
        if not record.exists():
            raise UserError(_("The source record no longer exists."))
        return record

    def action_generate(self):
        for document in self:
            record = document._get_record()
            header, body, footer = document.template_id.render(record)
            document.write({
                "record_name": record.display_name,
                "rendered_html": header + body + footer,
                "state": "draft",
            })
            report = self.env.ref("report_forge.action_report_forge")
            try:
                pdf, _ext = report._render_qweb_pdf(
                    "report_forge.report_forge", res_ids=document.ids)
            except TypeError:
                pdf, _ext = report._render_qweb_pdf(document.ids)
            attachment = self.env["ir.attachment"].create({
                "name": "%s.pdf" % document.name.replace("/", "-"),
                "raw": base64.b64encode(pdf),
                "mimetype": "application/pdf",
                "res_model": "report.forge.document",
                "res_id": document.id,
            })
            document.write({"state": "done", "attachment_id": attachment.id})
        return True

    def action_preview(self):
        return self.env.ref(
            "report_forge.action_report_forge").report_action(self)
