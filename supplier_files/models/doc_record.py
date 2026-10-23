# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models, _


class SupplierDocument(models.Model):
    _name = "supplier.document"
    _description = "Supplier Document"
    _inherit = ["mail.thread"]
    _order = "expiry_date asc"

    name = fields.Char(default="/", copy=False, readonly=True)
    partner_id = fields.Many2one("res.partner", required=True,
                                 ondelete="cascade")
    type_id = fields.Many2one("supplier.document.type", required=True,
                              ondelete="restrict")
    reference = fields.Char(string="Document Reference")
    issue_date = fields.Date()
    expiry_date = fields.Date()
    file_id = fields.Many2one("ir.attachment", string="Attached File",
                              ondelete="set null")
    verified = fields.Boolean(default=False)
    state = fields.Selection(
        [("draft", "To Provide"), ("valid", "Valid"), ("expiring", "Expiring"),
         ("expired", "Expired")],
        default="draft", compute="_compute_state", store=True)
    note = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "supplier.document") or "/"
        return super().create(vals_list)

    @api.depends("expiry_date", "verified")
    def _compute_state(self):
        today = date.today()
        for rec in self:
            if not rec.verified:
                rec.state = "draft"
            elif not rec.expiry_date:
                rec.state = "valid"
            elif rec.expiry_date < today:
                rec.state = "expired"
            else:
                days = (rec.expiry_date - today).days
                warn = rec.type_id.expiry_warning_days or 0
                rec.state = "expiring" if days <= warn else "valid"

    def action_verify(self):
        for rec in self:
            if not rec.expiry_date and rec.type_id.has_expiry:
                rec.message_post(body=_(
                    "Document verified without an expiry date."))
            rec.verified = True


class SupplierFileStatus(models.TransientModel):
    _name = "supplier.file.status"
    _description = "Supplier File Completeness"

    partner_id = fields.Many2one("res.partner", required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    missing_ids = fields.Many2many(
        "supplier.document.type",
        "supplier_file_status_missing_rel", "status_id", "type_id",
        string="Missing Documents")
    expired_ids = fields.Many2many(
        "supplier.document.type",
        "supplier_file_status_expired_rel", "status_id", "type_id",
        string="Expired Documents")
    blocking_ids = fields.Many2many(
        "supplier.document.type",
        "supplier_file_status_blocking_rel", "status_id", "type_id",
        string="Blocking Issues")
    complete = fields.Boolean(compute="_compute_status", store=True)
    score = fields.Integer(compute="_compute_status", store=True)
    blocking = fields.Boolean(compute="_compute_status", store=True)

    @api.depends("partner_id", "missing_ids", "expired_ids", "blocking_ids")
    def _compute_status(self):
        for rec in self:
            types = self.env["supplier.document.type"].search(
                [("required", "=", True), ("active", "=", True)])
            total = len(types)
            problems = rec.missing_ids | rec.expired_ids
            rec.score = int(round(100.0 * (total - len(problems)) / total)) \
                if total else 100
            rec.complete = not problems
            rec.blocking = bool(rec.blocking_ids)

    @api.model
    def evaluate_partner(self, partner):
        rec = self.create({"partner_id": partner.id})
        types = self.env["supplier.document.type"].search(
            [("required", "=", True), ("active", "=", True)])
        have = {d.type_id.id: d for d in self.env["supplier.document"].search(
            [("partner_id", "=", partner.id)])}
        missing, expired, blocking = [], [], []
        today = date.today()
        for doctype in types:
            doc = have.get(doctype.id)
            if not doc or not doc.verified:
                missing.append(doctype.id)
            elif doctype.has_expiry and doc.expiry_date and doc.expiry_date < today:
                expired.append(doctype.id)
            if doctype.blocking and (not doc or not doc.verified or
                                     (doctype.has_expiry and doc.expiry_date and
                                      doc.expiry_date < today)):
                blocking.append(doctype.id)
        rec.write({
            "missing_ids": [(6, 0, missing)],
            "expired_ids": [(6, 0, expired)],
            "blocking_ids": [(6, 0, blocking)],
        })
        return rec

    @api.model
    def _cron_check_all(self):
        partners = self.env["res.partner"].search(
            [("supplier_rank", ">", 0)])
        for partner in partners:
            rec = self.evaluate_partner(partner)
            if rec.blocking_ids:
                partner.message_post(body=_(
                    "File incomplete: %s") % ", ".join(
                        rec.blocking_ids.mapped("name")))
        return True