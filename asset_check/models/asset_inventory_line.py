# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AssetInventoryLine(models.Model):
    _name = "asset.inventory.line"
    _description = "Asset Count Line"
    _order = "inventory_id, asset_tag, id"

    inventory_id = fields.Many2one(
        "asset.inventory", string="Campaign", required=True,
        ondelete="cascade", index=True)
    asset_tag = fields.Char(required=True, help="Identifier on the asset label.")
    asset_name = fields.Char(
        string="Asset", required=True, help="Description of the asset to count.")
    expected_location = fields.Char(
        help="Location where the asset is expected according to the register.")
    observed_location = fields.Char(
        help="Location where the asset was actually found.")
    result = fields.Selection(
        [("found", "Found"), ("missing", "Missing"), ("moved", "Moved")],
        copy=False, index=True)
    checked_on = fields.Date()
    company_id = fields.Many2one(
        related="inventory_id.company_id", store=True, readonly=True,
        index=True)
    note = fields.Char()

    @api.constrains("result", "observed_location")
    def _check_moved_location(self):
        for line in self:
            if line.result == "moved" and not line.observed_location:
                raise ValidationError(_(
                    "Record the observed location for the moved asset %s.",
                    line.asset_tag))

    @api.model_create_multi
    def create(self, vals_list):
        inventory_ids = {vals.get("inventory_id") for vals in vals_list
                         if vals.get("inventory_id")}
        if inventory_ids:
            closed = self.env["asset.inventory"].browse(
                list(inventory_ids)).filtered(
                    lambda inventory: inventory.state == "closed")
            if closed:
                raise UserError(_(
                    "The closed campaign %s cannot receive new lines.",
                    closed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        if any(line.inventory_id.state == "closed" for line in self):
            raise UserError(_("A line on a closed campaign cannot be changed."))
        if vals.get("inventory_id"):
            target = self.env["asset.inventory"].browse(vals["inventory_id"])
            if target.state == "closed":
                raise UserError(_(
                    "The closed campaign %s cannot receive new lines.",
                    target.name))
        return super().write(vals)
