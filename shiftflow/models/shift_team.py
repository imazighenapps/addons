from odoo import fields, models

class ShiftFlowTeam(models.Model):
    _name = "shiftflow.team"
    _description = "Shift Team"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    manager_id = fields.Many2one("res.users", string="Team Manager")
    member_ids = fields.Many2many("res.users", string="Members")
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    notes = fields.Text(translate=True)
