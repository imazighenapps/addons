from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleMarginRule(models.Model):
    _name = "sale.margin.rule"
    _description = "Sale Margin Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    min_margin_percent = fields.Float(
        string="Minimum Margin (%)",
        required=True,
        help="Sale orders matching this rule's scope will be blocked on "
             "confirmation if their margin is below this percentage.",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        help="Leave empty to apply this rule to all companies.",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        domain="[('customer_rank', '>', 0)]",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product Variant",
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        help="Use this instead of 'Product Variant' to target every "
             "variant of a product at once.",
    )
    categ_id = fields.Many2one(
        "product.category",
        string="Product Category",
    )

    _sql_constraints = [
        (
            "check_min_margin_percent",
            "CHECK(min_margin_percent <= 100)",
            "The minimum margin cannot exceed 100%.",
        ),
    ]

    @api.constrains("product_id", "product_tmpl_id", "categ_id", "partner_id")
    def _check_scope(self):
        for rule in self:
            if rule.product_id and rule.product_tmpl_id:
                raise ValidationError(_(
                    "Rule '%s': choose either a Product Variant or a "
                    "Product Template, not both."
                ) % rule.name)
            if not (rule.product_id or rule.product_tmpl_id
                    or rule.categ_id or rule.partner_id):
                raise ValidationError(_(
                    "Rule '%s': please set at least one scope (Product, "
                    "Product Template, Category or Customer). Use the "
                    "'Default Minimum Margin' setting instead for a rule "
                    "without any scope."
                ) % rule.name)
