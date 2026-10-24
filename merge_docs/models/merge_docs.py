# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DocMerge(models.Model):
    _name = "doc.merge"
    _description = "Document Dossier"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    date_from = fields.Date()
    date_to = fields.Date()
    include_quotes = fields.Boolean(string="Quotations", default=True)
    include_orders = fields.Boolean(string="Confirmed Orders", default=True)
    include_invoices = fields.Boolean(string="Invoices", default=True)
    include_deliveries = fields.Boolean(string="Delivery Notes", default=True)
    line_ids = fields.One2many("doc.merge.line", "merge_id", string="Documents")
    document_count = fields.Integer(compute="_compute_count", store=True)
    total_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_count", store=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    cover_page = fields.Boolean(default=True)
    toc = fields.Boolean(string="Table of Contents", default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("loaded", "Loaded"), ("done", "Generated")],
        default="draft", required=True, tracking=True)
    attachment_id = fields.Many2one("ir.attachment", string="Generated PDF")
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "doc.merge") or "/"
        return super().create(vals_list)

    @api.depends("line_ids", "line_ids.amount")
    def _compute_count(self):
        for merge in self:
            merge.document_count = len(merge.line_ids)
            merge.total_amount = sum(merge.line_ids.mapped("amount"))

    def _snapshot(self, record):
        if record._name == "stock.picking":
            lines = record.move_ids
            rows = []
            for move in lines:
                rows.append(
                    "<tr><td>" + (move.product_id.display_name or "") + "</td>"
                    "<td style='text-align:right'>" + str(move.product_uom_qty)
                    + "</td></tr>")
            return ("<table class='table table-sm' style='width:100%'>"
                    "<thead><tr><th>Product</th><th style='text-align:right'>Qty</th>"
                    "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")
        if "order_line" in record._fields:
            lines = record.order_line
        elif "invoice_line_ids" in record._fields:
            lines = record.invoice_line_ids
        else:
            return ""
        rows = []
        for line in lines:
            label = line.product_id.display_name if "product_id" in line._fields \
                else (line.name or "")
            qty = line.quantity if "quantity" in line._fields \
                else line.product_uom_qty
            rows.append(
                "<tr><td>" + (label or "") + "</td>"
                "<td style='text-align:right'>" + str(qty) + "</td>"
                "<td style='text-align:right'>" + "{:,.2f}".format(
                    line.price_unit) + "</td>"
                "<td style='text-align:right'>" + "{:,.2f}".format(
                    line.price_subtotal) + "</td></tr>")
        return ("<table class='table table-sm' style='width:100%'>"
                "<thead><tr><th>Description</th>"
                "<th style='text-align:right'>Qty</th>"
                "<th style='text-align:right'>Unit</th>"
                "<th style='text-align:right'>Subtotal</th></tr></thead>"
                "<tbody>" + "".join(rows) + "</tbody></table>")

    def _add_line(self, record, label, amount, doc_date):
        self.env["doc.merge.line"].create({
            "merge_id": self.id,
            "model_name": record._name,
            "res_id": record.id,
            "label": label,
            "reference": record.display_name,
            "document_date": doc_date,
            "amount": amount,
            "snapshot_html": self._snapshot(record),
        })

    def action_load(self):
        for merge in self:
            if not merge.partner_id:
                raise UserError(_("Select a customer first."))
            merge.line_ids.unlink()
            date_from = merge.date_from or "1900-01-01"
            date_to = merge.date_to or "2100-12-31"
            if merge.include_quotes or merge.include_orders:
                states = []
                if merge.include_quotes:
                    states += ["draft", "sent"]
                if merge.include_orders:
                    states += ["sale", "done"]
                orders = self.env["sale.order"].search([
                    ("partner_id", "=", merge.partner_id.id),
                    ("state", "in", states),
                    ("date_order", ">=", date_from),
                    ("date_order", "<=", date_to),
                ], order="date_order")
                for order in orders:
                    label = _("Quotation") if order.state in ("draft", "sent") \
                        else _("Sales Order")
                    merge._add_line(order, label, order.amount_total,
                                    order.date_order)
            if merge.include_invoices:
                invoices = self.env["account.move"].search([
                    ("partner_id", "=", merge.partner_id.id),
                    ("move_type", "in", ["out_invoice", "out_refund"]),
                    ("state", "!=", "cancel"),
                    ("invoice_date", ">=", date_from),
                    ("invoice_date", "<=", date_to),
                ], order="invoice_date")
                for invoice in invoices:
                    label = _("Credit Note") if invoice.move_type == "out_refund" \
                        else _("Invoice")
                    merge._add_line(invoice, label, invoice.amount_total,
                                    invoice.invoice_date)
            if merge.include_deliveries:
                pickings = self.env["stock.picking"].search([
                    ("partner_id", "=", merge.partner_id.id),
                    ("state", "=", "done"),
                    ("date_done", ">=", date_from),
                    ("date_done", "<=", date_to),
                ], order="date_done")
                for picking in pickings:
                    merge._add_line(picking, _("Delivery"), 0.0,
                                    picking.date_done)
            merge.state = "loaded" if merge.line_ids else "draft"
            if not merge.line_ids:
                raise UserError(_("No document found for this customer and period."))
        return True

    def _render(self):
        self.ensure_one()
        report = self.env.ref("merge_docs.action_report_doc_merge")
        try:
            pdf, _ext = report._render_qweb_pdf(
                "merge_docs.report_doc_merge", res_ids=self.ids)
        except TypeError:
            pdf, _ext = report._render_qweb_pdf(self.ids)
        return pdf

    def action_generate(self):
        for merge in self:
            if not merge.line_ids:
                raise UserError(_("Load the documents before generating the PDF."))
            pdf = merge._render()
            attachment = self.env["ir.attachment"].create({
                "name": "%s.pdf" % merge.name.replace("/", "-"),
                "raw": base64.b64encode(pdf),
                "mimetype": "application/pdf",
                "res_model": "doc.merge",
                "res_id": merge.id,
            })
            merge.write({"state": "done", "attachment_id": attachment.id})
            merge.message_post(body=_(
                "%s documents merged.", merge.document_count))
        return True

    def action_preview(self):
        return self.env.ref(
            "merge_docs.action_report_doc_merge").report_action(self)


class DocMergeLine(models.Model):
    _name = "doc.merge.line"
    _description = "Dossier Line"
    _order = "document_date, id"

    merge_id = fields.Many2one(
        "doc.merge", required=True, ondelete="cascade", index=True)
    model_name = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    label = fields.Char()
    reference = fields.Char()
    document_date = fields.Datetime()
    amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        related="merge_id.currency_id", store=True, readonly=True)
    snapshot_html = fields.Html(readonly=True)
