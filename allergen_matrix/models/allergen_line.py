# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AllergenLine(models.Model):
    _name = "allergen.line"
    _description = "Allergen Line"
    _order = "recipe_id, allergen, id"

    recipe_id = fields.Many2one(
        "allergen.recipe", string="Recipe", required=True,
        ondelete="cascade", index=True)
    allergen = fields.Selection(
        [("gluten", "Gluten"), ("crustaceans", "Crustaceans"),
         ("eggs", "Eggs"), ("fish", "Fish"), ("peanuts", "Peanuts"),
         ("soy", "Soy"), ("milk", "Milk"), ("nuts", "Tree Nuts"),
         ("celery", "Celery"), ("mustard", "Mustard"),
         ("sesame", "Sesame"), ("sulphites", "Sulphites"),
         ("lupin", "Lupin"), ("molluscs", "Molluscs")],
        required=True,
        help="Declared allergen covered by this line.")
    presence = fields.Selection(
        [("present", "Present"), ("cross", "Cross-Contact")],
        default="present", required=True,
        help="Whether the allergen is an ingredient or a cross-contact risk.")
    source = fields.Char(
        help="Ingredient or process step at the origin of the allergen.")
    company_id = fields.Many2one(
        related="recipe_id.company_id", store=True, readonly=True)

    _sql_constraints = [
        ('recipe_allergen_uniq', "UNIQUE(recipe_id, allergen)", "Each allergen can only be declared once per recipe."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        recipe_ids = {v["recipe_id"] for v in vals_list if v.get("recipe_id")}
        if recipe_ids:
            locked = self.env["allergen.recipe"].browse(
                sorted(recipe_ids)).filtered(
                lambda r: r.state == "validated")
            if locked:
                raise UserError(_(
                    "The recipe \"%s\" is validated: no allergen line can "
                    "be added to it.", locked[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.recipe_id.state == "validated":
                raise UserError(_(
                    "The recipe \"%s\" is validated: its allergen lines can "
                    "no longer be changed.", line.recipe_id.name))
        if vals.get("recipe_id"):
            target = self.env["allergen.recipe"].browse(vals["recipe_id"])
            if target.state == "validated":
                raise UserError(_(
                    "The recipe \"%s\" is validated: no line can be moved "
                    "to it.", target.name))
        return super().write(vals)

    def unlink(self):
        for line in self:
            if line.recipe_id.state == "validated":
                raise UserError(_(
                    "The recipe \"%s\" is validated: its allergen lines can "
                    "no longer be removed.", line.recipe_id.name))
        return super().unlink()
