# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AuditBinderItem(models.Model):
    _name = "audit.binder.item"
    _description = "Audit Evidence Item"
    _inherit = ["mail.thread"]
    _order = "section_name, id"

    name = fields.Char(required=True, tracking=True,
                       help="Short title of the evidence item.")
    binder_id = fields.Many2one(
        "audit.binder", string="Binder", required=True,
        ondelete="cascade", index=True, tracking=True)
    section_name = fields.Char(
        string="Section", required=True, tracking=True,
        help="Account or topic this evidence belongs to.")
    reference = fields.Char(
        help="Document, entry or reconciliation reference for this item.")
    description = fields.Text(
        help="What this item proves and where it comes from.")
    ready = fields.Boolean(
        default=False, tracking=True,
        help="Ticked once the evidence is collected and attached.")
    company_id = fields.Many2one(
        related="binder_id.company_id", store=True, readonly=True, index=True)
    state = fields.Selection(
        related="binder_id.state", store=True, readonly=True)

    @api.constrains("ready", "reference")
    def _check_reference(self):
        for item in self:
            if item.ready and not (item.reference and item.reference.strip()):
                raise ValidationError(_(
                    "Provide a reference for %s before marking it as ready.",
                    item.name))

    def action_mark_ready(self):
        for item in self:
            if item.binder_id.state == "closed":
                raise ValidationError(_(
                    "A closed binder cannot accept new ready items."))
            item.ready = True
            item.message_post(body=_(
                "The evidence item was marked as ready."))
        return True
