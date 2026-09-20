from odoo import fields, models

class ShiftFlowLog(models.Model):
    _name = "shiftflow.log"
    _description = "Shift Log Entry"
    _inherit = ["mail.thread"]
    _order = "occurred_at desc"

    name = fields.Char(required=True, translate=True)
    shift_id = fields.Many2one("shiftflow.shift", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="shift_id.company_id", store=True, index=True)
    occurred_at = fields.Datetime(required=True, default=fields.Datetime.now)
    author_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    entry_type = fields.Selection([("note", "Note"), ("event", "Event"), ("observation", "Observation"), ("info", "Information")], default="note", required=True)
    priority = fields.Selection([("low", "Low"), ("normal", "Normal"), ("high", "High"), ("critical", "Critical")], default="normal", required=True)
    description = fields.Text(required=True, translate=True)
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
