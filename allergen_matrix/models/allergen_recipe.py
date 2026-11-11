# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AllergenRecipe(models.Model):
    _name = "allergen.recipe"
    _description = "Allergen Recipe"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    product_name = fields.Char(
        string="Product", required=True, tracking=True,
        help="Finished product covered by this allergen declaration.")
    line_name = fields.Char(
        string="Production Line",
        help="Line or area where cross-contact may occur.")
    declaration_ref = fields.Char(
        string="Declaration Reference",
        help="Reference of the label or declaration document.")
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated"),
         ("archived", "Archived")],
        default="draft", required=True, copy=False,
        tracking=True, index=True)
    line_ids = fields.One2many(
        "allergen.line", "recipe_id", string="Allergens", copy=True)
    allergen_count = fields.Integer(
        string="Allergen Lines", compute="_compute_counts", store=True)
    present_count = fields.Integer(
        string="Present", compute="_compute_counts", store=True,
        help="Number of allergens present as ingredients.")
    cross_count = fields.Integer(
        string="Cross-Contact", compute="_compute_counts", store=True,
        help="Number of allergens possible through cross-contact.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids.presence")
    def _compute_counts(self):
        for recipe in self:
            recipe.allergen_count = len(recipe.line_ids)
            recipe.present_count = len(recipe.line_ids.filtered(
                lambda l: l.presence == "present"))
            recipe.cross_count = len(recipe.line_ids.filtered(
                lambda l: l.presence == "cross"))

    def action_validate(self):
        for recipe in self:
            if recipe.state != "draft":
                raise UserError(_("Only a draft recipe can be validated."))
            if not recipe.line_ids:
                raise UserError(_(
                    "Add at least one allergen line before validating %s.",
                    recipe.name))
            recipe.state = "validated"
            recipe.message_post(body=_(
                "Allergen declaration validated with %s allergen line(s).",
                recipe.allergen_count))
        return True

    def action_archive_recipe(self):
        for recipe in self:
            if recipe.state != "validated":
                raise UserError(
                    _("Only a validated recipe can be archived."))
            recipe.state = "archived"
            recipe.message_post(body=_("Recipe archived."))
        return True

    def action_reset(self):
        for recipe in self:
            if recipe.state == "draft":
                raise UserError(_("The recipe is already in draft."))
            recipe.state = "draft"
            recipe.message_post(body=_("Recipe reset to draft."))
        return True

    def write(self, vals):
        locked = {"name", "product_name", "line_name", "declaration_ref"}
        if locked & set(vals):
            for recipe in self:
                if recipe.state == "validated":
                    raise UserError(_(
                        "The validated recipe \"%s\" can no longer be "
                        "changed. Reset it to draft first.", recipe.name))
        return super().write(vals)
