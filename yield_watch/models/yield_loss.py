# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class YieldLoss(models.Model):
    _name = "yield.loss"
    _description = "Production Loss Line"
    _order = "run_id, sequence, id"

    run_id = fields.Many2one(
        "yield.run", string="Run", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    reason = fields.Char(
        required=True, help="Named cause of the loss, for example Scrap.")
    step = fields.Char(
        help="Production step where the loss occurred.")
    quantity = fields.Float(
        required=True, help="Quantity lost for this reason.")
    company_id = fields.Many2one(
        related="run_id.company_id", store=True, readonly=True)
    note = fields.Char()

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_(
                    "The quantity lost on \"%s\" must be above zero.",
                    line.reason))

    @api.model_create_multi
    def create(self, vals_list):
        run_ids = {vals["run_id"] for vals in vals_list if vals.get("run_id")}
        if run_ids:
            closed = self.env["yield.run"].browse(sorted(run_ids)).filtered(
                lambda run: run.state == "closed")
            if closed:
                raise UserError(_(
                    "The run \"%s\" is closed: no loss line can be added "
                    "to it.", closed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.run_id.state == "closed":
                raise UserError(_(
                    "The run \"%s\" is closed: its loss lines can no longer "
                    "be changed.", line.run_id.name))
        if vals.get("run_id"):
            target = self.env["yield.run"].browse(vals["run_id"])
            if target.state == "closed":
                raise UserError(_(
                    "The run \"%s\" is closed: no line can be moved to it.",
                    target.name))
        return super().write(vals)
