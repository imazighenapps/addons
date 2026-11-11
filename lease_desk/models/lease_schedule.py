# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LeaseSchedule(models.Model):
    _name = "lease.schedule"
    _description = "Lease Schedule Line"
    _order = "lease_id, sequence, due_date, id"

    lease_id = fields.Many2one(
        "lease.contract", string="Lease", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    due_date = fields.Date(required=True, index=True)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(
        related="lease_id.currency_id", store=True, readonly=True)
    state = fields.Selection(
        [("pending", "Pending"), ("posted", "Posted")],
        default="pending", required=True, copy=False, index=True)
    posted_on = fields.Date(string="Posted On", readonly=True, copy=False)
    company_id = fields.Many2one(
        related="lease_id.company_id", store=True, readonly=True)

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError(_(
                    "The amount of a schedule line must be greater than zero."))

    def action_post(self):
        for line in self:
            if line.lease_id.state == "draft":
                raise UserError(_(
                    "Start the lease before posting schedule lines."))
            if line.state == "posted":
                raise UserError(_(
                    "This schedule line is already posted."))
            line.write({
                "state": "posted",
                "posted_on": fields.Date.context_today(line),
            })
        return True

    @api.model_create_multi
    def create(self, vals_list):
        lease_ids = {v["lease_id"] for v in vals_list if v.get("lease_id")}
        if lease_ids:
            closed = self.env["lease.contract"].browse(
                sorted(lease_ids)).filtered(lambda l: l.state == "closed")
            if closed:
                raise UserError(_(
                    "Lease %s is closed: no schedule line can be added.",
                    closed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.lease_id.state == "closed":
                raise UserError(_(
                    "Lease %s is closed: its schedule cannot be changed.",
                    line.lease_id.name))
        return super().write(vals)
