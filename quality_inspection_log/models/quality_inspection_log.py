# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class QualityInspectionLog(models.Model):
    _name = "quality.inspection.log"
    _description = "Quality Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "inspection_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, index=True,
        tracking=True)
    picking_id = fields.Many2one(
        "stock.picking", string="Transfer", tracking=True)
    inspection_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    inspector_id = fields.Many2one(
        "res.users", string="Inspector", default=lambda self: self.env.user,
        tracking=True)
    result = fields.Selection(
        [("pending", "Pending"), ("pass", "Pass"), ("fail", "Fail")],
        default="pending", required=True, tracking=True)
    criteria = fields.Text(string="Criteria / Checklist")
    observations = fields.Text()
    corrective_action = fields.Text(string="Corrective Action")
    state = fields.Selection(
        [("draft", "Draft"), ("progress", "In Progress"),
         ("passed", "Passed"), ("failed", "Failed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("quality.inspection.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_start(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft inspection can be started."))
            record.state = "progress"
        return True

    def action_pass(self):
        for record in self:
            if record.state != "progress":
                raise UserError(_("Only an inspection in progress can be marked passed."))
            record.write({"state": "passed", "result": "pass"})
        return True

    def action_fail(self):
        for record in self:
            if record.state != "progress":
                raise UserError(_("Only an inspection in progress can be marked failed."))
            record.write({"state": "failed", "result": "fail"})
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("passed", "failed", "cancelled"):
                raise UserError(_("A completed or cancelled inspection cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("cancelled", "failed"):
                raise UserError(_("Only a cancelled or failed inspection can be reset to draft."))
            record.write({"state": "draft", "result": "pending"})
        return True
