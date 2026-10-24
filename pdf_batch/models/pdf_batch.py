# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PdfBatch(models.Model):
    _name = "pdf.batch"
    _description = "PDF Batch"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Customer")
    date = fields.Date(default=fields.Date.context_today, required=True)
    date_from = fields.Date()
    date_to = fields.Date()
    invoice_ids = fields.Many2many(
        "account.move", "pdf_batch_move_rel", "batch_id", "move_id",
        string="Documents",
        domain=[("move_type", "in", ["out_invoice", "out_refund"])])
    invoice_count = fields.Integer(compute="_compute_totals", store=True)
    total_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    watermark = fields.Char(
        help="Text printed diagonally on every page, for example DRAFT or COPY.")
    cover_page = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Generated")],
        default="draft", required=True, tracking=True)
    attachment_id = fields.Many2one("ir.attachment", string="Generated PDF")
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "pdf.batch") or "/"
        return super().create(vals_list)

    @api.depends("invoice_ids", "invoice_ids.amount_total")
    def _compute_totals(self):
        for batch in self:
            batch.invoice_count = len(batch.invoice_ids)
            batch.total_amount = sum(batch.invoice_ids.mapped("amount_total"))

    def _render(self):
        self.ensure_one()
        report = self.env.ref("pdf_batch.action_report_pdf_batch")
        try:
            pdf, _ext = report._render_qweb_pdf(
                "pdf_batch.report_pdf_batch", res_ids=self.ids)
        except TypeError:
            pdf, _ext = report._render_qweb_pdf(self.ids)
        return pdf

    def action_generate(self):
        for batch in self:
            if not batch.invoice_ids:
                raise UserError(_("Select at least one document."))
            pdf = batch._render()
            filename = "%s.pdf" % (batch.name or "batch").replace("/", "-")
            attachment = self.env["ir.attachment"].create({
                "name": filename,
                "raw": base64.b64encode(pdf),
                "mimetype": "application/pdf",
                "res_model": "pdf.batch",
                "res_id": batch.id,
            })
            batch.write({"state": "done", "attachment_id": attachment.id})
            batch.message_post(body=_(
                "%(count)s documents merged into %(file)s.",
                count=batch.invoice_count, file=filename))
        return True

    def action_preview(self):
        return self.env.ref(
            "pdf_batch.action_report_pdf_batch").report_action(self)

    def action_reset(self):
        self.write({"state": "draft", "attachment_id": False})


class AccountMove(models.Model):
    _inherit = "account.move"

    pdf_batch_ids = fields.Many2many(
        "pdf.batch", "pdf_batch_move_rel", "move_id", "batch_id",
        string="PDF Batches")
