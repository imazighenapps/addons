# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SdsVersion(models.Model):
    _name = "sds.version"
    _description = "Safety Data Sheet Version"
    _inherit = ["mail.thread"]
    _order = "issue_date desc, id desc"

    name = fields.Char(
        required=True,
        help="Reference or revision number of the sheet.")
    product_id = fields.Many2one(
        "sds.product", string="Chemical Product", required=True,
        ondelete="cascade", index=True, tracking=True)
    issue_date = fields.Date(
        string="Issue Date", required=True,
        default=fields.Date.context_today, tracking=True)
    expiry_date = fields.Date(
        string="Expiry Date", required=True, tracking=True)
    supplier_ref = fields.Char(
        string="Supplier Reference",
        help="Reference given by the supplier for this revision.")
    is_current = fields.Boolean(
        string="Current", default=False, tracking=True,
        help="Marked when this version is the current sheet.")
    company_id = fields.Many2one(
        related="product_id.company_id", store=True, readonly=True)
    note = fields.Text()

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        for version in self:
            if version.expiry_date < version.issue_date:
                raise ValidationError(_(
                    "The expiry date of version %s cannot come before its "
                    "issue date.", version.name))

    def action_mark_current(self):
        for version in self:
            siblings = self.search([
                ("product_id", "=", version.product_id.id),
                ("is_current", "=", True),
                ("id", "!=", version.id),
            ])
            siblings.write({"is_current": False})
            version.write({"is_current": True})
            version.product_id.write({
                "current_issue": version.issue_date,
                "current_expiry": version.expiry_date,
            })
            version.message_post(body=_(
                "Version marked as the current safety data sheet."))
        return True
