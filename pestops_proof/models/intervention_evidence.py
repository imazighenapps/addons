from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import hashlib
import base64


class PestInterventionEvidence(models.Model):
    _name = "pest.intervention.evidence"
    _description = "PestOps Intervention Evidence"
    _order = "proof_id, sequence, id"

    proof_id = fields.Many2one(
        "pest.intervention.proof", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    category = fields.Selection([
        ("before", "Before"),
        ("during", "During"),
        ("after", "After"),
        ("other", "Other"),
    ], required=True, default="before", index=True)
    title = fields.Char(required=True)
    image = fields.Binary(required=True, attachment=True)
    captured_at = fields.Datetime(default=fields.Datetime.now, required=True)
    captured_by = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True
    )
    note = fields.Text()
    sha256 = fields.Char(string="Evidence Hash", readonly=True, copy=False)
    mime_type = fields.Char(readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._refresh_fingerprint()
        return records

    def write(self, vals):
        result = super().write(vals)
        if any(k in vals for k in ("image", "title", "category", "captured_at")):
            for rec in self:
                rec._refresh_fingerprint()
        return result

    def _refresh_fingerprint(self):
        for rec in self:
            if rec.image:
                raw = base64.b64decode(rec.image)
                rec.sha256 = hashlib.sha256(raw).hexdigest()
                if not rec.mime_type:
                    rec.mime_type = "image/png"

    @api.constrains("image")
    def _check_image(self):
        for rec in self:
            if not rec.image:
                raise ValidationError(_("Evidence must contain an image."))
