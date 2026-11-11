# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LotGenealogyLink(models.Model):
    _name = "lot.genealogy.link"
    _description = "Lot Genealogy Link"
    _order = "parent_lot_id, child_lot_id, id"

    parent_lot_id = fields.Many2one(
        "lot.genealogy", string="Parent Lot", required=True,
        ondelete="cascade", index=True)
    child_lot_id = fields.Many2one(
        "lot.genealogy", string="Child Lot", required=True,
        ondelete="cascade", index=True)
    quantity = fields.Float(default=1.0)
    linked_on = fields.Date(
        string="Linked On", default=fields.Date.context_today, required=True)
    note = fields.Char()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.constrains("parent_lot_id", "child_lot_id")
    def _check_link(self):
        for link in self:
            if link.parent_lot_id == link.child_lot_id:
                raise ValidationError(_(
                    "A lot cannot be its own parent."))
            if link.parent_lot_id.company_id != link.child_lot_id.company_id:
                raise ValidationError(_(
                    "Parent and child lots must belong to the same company."))
            dup = self.search_count([
                ("parent_lot_id", "=", link.parent_lot_id.id),
                ("child_lot_id", "=", link.child_lot_id.id),
                ("id", "!=", link.id),
            ])
            if dup:
                raise ValidationError(_(
                    "This parent-child link already exists."))

    @api.constrains("quantity")
    def _check_quantity(self):
        for link in self:
            if link.quantity <= 0:
                raise ValidationError(_(
                    "The linked quantity must be greater than zero."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("parent_lot_id") and not vals.get("company_id"):
                parent = self.env["lot.genealogy"].browse(vals["parent_lot_id"])
                vals["company_id"] = parent.company_id.id
        return super().create(vals_list)
