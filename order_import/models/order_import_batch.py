# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OrderImportBatch(models.Model):
    _name = "order.import.batch"
    _description = "Order Import Batch"
    _inherit = ["mail.thread"]
    _order = "import_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        index=True)
    import_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    source_file = fields.Char(
        string="Source File",
        help="Name of the customer file that produced this batch.")
    line_ids = fields.One2many(
        "order.import.line", "batch_id", string="Lines")
    line_count = fields.Integer(
        string="Lines", compute="_compute_counts", store=True)
    accepted_count = fields.Integer(
        string="Accepted", compute="_compute_counts", store=True)
    rejected_count = fields.Integer(
        string="Rejected", compute="_compute_counts", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated"),
         ("processed", "Processed")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.status")
    def _compute_counts(self):
        for batch in self:
            lines = batch.line_ids
            batch.line_count = len(lines)
            batch.accepted_count = len(lines.filtered(
                lambda line: line.status == "accepted"))
            batch.rejected_count = len(lines.filtered(
                lambda line: line.status == "rejected"))

    @api.constrains("line_ids")
    def _check_has_lines(self):
        for batch in self:
            if not batch.line_ids:
                raise ValidationError(_(
                    "The import batch %s must contain at least one line.",
                    batch.name))

    def action_validate(self):
        for batch in self:
            for line in batch.line_ids:
                if not line.product_ref or line.quantity <= 0:
                    line.write({
                        "status": "rejected",
                        "error_message": _(
                            "Provide a product reference and a quantity above "
                            "zero."),
                    })
                else:
                    line.write({"status": "accepted", "error_message": False})
            batch.write({"state": "validated"})
            batch.message_post(body=_(
                "Batch validated: %s accepted, %s rejected.",
                batch.accepted_count, batch.rejected_count))
        return True

    def action_process(self):
        for batch in self:
            if batch.state != "validated":
                raise ValidationError(_(
                    "Validate the batch %s before processing it.", batch.name))
            batch.write({"state": "processed"})
            batch.message_post(body=_("The batch has been marked processed."))
        return True
