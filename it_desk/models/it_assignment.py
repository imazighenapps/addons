# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ItAssignment(models.Model):
    _name = "it.assignment"
    _description = "IT Assignment"
    _inherit = ["mail.thread"]
    _order = "assigned_on desc, id desc"

    name = fields.Char(
        required=True, compute="_compute_name", store=True,
        precompute=True)
    asset_id = fields.Many2one(
        "it.asset", string="Asset", required=True, ondelete="cascade",
        index=True, tracking=True)
    holder = fields.Char(
        required=True, tracking=True,
        help="Person or team currently holding the asset.")
    assigned_on = fields.Date(
        string="Assigned On", required=True,
        default=fields.Date.context_today, tracking=True)
    due_back_on = fields.Date(
        string="Due Back On", tracking=True,
        help="Expected date the asset must be returned.")
    returned_on = fields.Date(
        string="Returned On", readonly=True, copy=False, tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("returned", "Returned")],
        default="open", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("asset_id", "holder", "assigned_on")
    def _compute_name(self):
        for assignment in self:
            asset = assignment.asset_id.name or _("Asset")
            holder = assignment.holder or _("Holder")
            day = assignment.assigned_on or fields.Date.context_today(assignment)
            assignment.name = _("%s - %s (%s)") % (asset, holder, day)

    @api.constrains("assigned_on", "due_back_on", "returned_on")
    def _check_dates(self):
        for assignment in self:
            if assignment.due_back_on and assignment.assigned_on \
                    and assignment.due_back_on < assignment.assigned_on:
                raise ValidationError(_(
                    "The due-back date of \"%s\" cannot be before the "
                    "assignment date.", assignment.name))
            if assignment.returned_on and assignment.assigned_on \
                    and assignment.returned_on < assignment.assigned_on:
                raise ValidationError(_(
                    "The return date of \"%s\" cannot be before the "
                    "assignment date.", assignment.name))

    def action_return(self):
        for assignment in self:
            if assignment.state != "open":
                raise UserError(_(
                    "Only an open assignment can be returned."))
            assignment.write({
                "state": "returned",
                "returned_on": fields.Date.context_today(assignment),
            })
            assignment.asset_id.write({"state": "stock"})
            assignment.message_post(body=_("The asset has been returned."))
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for assignment in records:
            if assignment.state == "open":
                assignment.asset_id.write({"state": "in_use"})
        return records
