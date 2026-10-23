# -*- coding: utf-8 -*-
import base64
import hashlib
from odoo import api, fields, models


class QesDocument(models.Model):
    _name = "qes.document"
    _description = "QES Document to Sign"

    envelope_id = fields.Many2one("qes.envelope", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    attachment_id = fields.Many2one("ir.attachment", string="Source File", required=True)
    provider_doc_id = fields.Char(string="Provider Document ID", copy=False)
    sha256_origin = fields.Char(compute="_compute_hashes", store=True)
    pades_level = fields.Selection(
        [("b-b", "PAdES B-B"), ("b-t", "PAdES B-T"),
         ("b-lt", "PAdES B-LT"), ("b-lta", "PAdES B-LTA")],
        default="b-t",
    )
    field_ids = fields.One2many("qes.field", "document_id", string="Fields")

    @api.depends("attachment_id.raw")
    def _compute_hashes(self):
        for rec in self:
            raw = rec.attachment_id.raw or b""
            try:
                blob = base64.b64decode(raw)
            except Exception:
                blob = b""
            rec.sha256_origin = hashlib.sha256(blob).hexdigest()
