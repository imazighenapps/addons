# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ForkliftCheck(models.Model):
    _name = "forklift.check"
    _description = "Forklift Safety Check"
    _inherit = ["mail.thread"]
    _order = "check_date desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Check %s")
        % fields.Date.context_today(self), tracking=True,
        help="Reference of the daily safety check.")
    truck_ref = fields.Char(
        string="Forklift", required=True, tracking=True,
        help="Identifier of the forklift being inspected.")
    operator_name = fields.Char(
        string="Operator", required=True, tracking=True,
        help="Name of the operator running the inspection.")
    check_date = fields.Date(
        string="Check Date", required=True,
        default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"),
         ("grounded", "Grounded")],
        default="draft", required=True, tracking=True, index=True)
    defect_ids = fields.One2many(
        "forklift.defect", "check_id", string="Defects")
    defect_count = fields.Integer(
        string="Defects", compute="_compute_defects", store=True)
    open_defect_count = fields.Integer(
        string="Open Defects", compute="_compute_defects", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("defect_ids", "defect_ids.state")
    def _compute_defects(self):
        for check in self:
            check.defect_count = len(check.defect_ids)
            check.open_defect_count = len(check.defect_ids.filtered(
                lambda defect: defect.state == "open"))

    def action_validate(self):
        for check in self:
            if check.state != "draft":
                raise ValidationError(_(
                    "The safety check %s has already been validated.",
                    check.name))
            target = "grounded" if check.open_defect_count else "ready"
            check.write({"state": target})
            check.message_post(body=_(
                "The safety check has been validated."))
        return True

    def action_reopen(self):
        for check in self:
            if check.state == "draft":
                raise ValidationError(_(
                    "The safety check %s is already in draft.", check.name))
            check.write({"state": "draft"})
            check.message_post(body=_(
                "The safety check has been reopened."))
        return True
