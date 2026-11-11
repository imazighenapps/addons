# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CertRenewal(models.Model):
    _name = "cert.renewal"
    _description = "Certificate Renewal"
    _order = "renewed_on desc, id desc"

    certificate_id = fields.Many2one(
        "cert.document", string="Certificate", required=True,
        ondelete="cascade", index=True)
    renewed_on = fields.Date(
        required=True, default=fields.Date.context_today)
    previous_expiry_date = fields.Date(string="Previous Expiry")
    new_issue_date = fields.Date(string="New Issue Date", required=True)
    new_expiry_date = fields.Date(string="New Expiry Date", required=True)
    company_id = fields.Many2one(
        "res.company", related="certificate_id.company_id", store=True,
        readonly=True, index=True)

    @api.constrains("new_issue_date", "new_expiry_date")
    def _check_dates(self):
        for renewal in self:
            if renewal.new_expiry_date < renewal.new_issue_date:
                raise ValidationError(_(
                    "The new expiry date of the renewal for %s cannot come "
                    "before the new issue date.",
                    renewal.certificate_id.name))
