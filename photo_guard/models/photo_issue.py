# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PhotoIssue(models.Model):
    _name = "photo.issue"
    _description = "Photo Issue"
    _inherit = ["mail.thread"]
    _order = "id"

    audit_id = fields.Many2one(
        "photo.audit", required=True, ondelete="cascade", index=True)
    product_name = fields.Char(string="Product", required=True, tracking=True)
    issue_type = fields.Selection(
        [("missing", "Missing"), ("weak", "Weak Quality"),
         ("outdated", "Outdated")],
        required=True, default="missing", tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("fixed", "Fixed")],
        default="open", required=True, tracking=True, index=True)
    fixed_on = fields.Date(string="Fixed On", readonly=True, copy=False)
    company_id = fields.Many2one(
        related="audit_id.company_id", store=True, readonly=True, index=True)
    note = fields.Text()

    def action_fix(self):
        for issue in self:
            if issue.state != "open":
                raise UserError(_(
                    "Issue %s is already fixed.", issue.product_name))
            issue.write({
                "state": "fixed",
                "fixed_on": fields.Date.context_today(issue),
            })
            issue.message_post(body=_("The photo issue was fixed."))
        return True
