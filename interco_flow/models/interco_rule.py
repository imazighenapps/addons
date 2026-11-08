# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class IntercoRule(models.Model):
    _name = "interco.rule"
    _description = "Intercompany Rule"
    _order = "company_id, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", string="Selling Company", required=True,
        default=lambda self: self.env.company)
    target_company_id = fields.Many2one(
        "res.company", string="Buying Company", required=True)
    vendor_partner_id = fields.Many2one(
        "res.partner", string="Vendor Partner",
        help="Partner used as vendor on the purchase order. Defaults to the "
             "partner of the selling company.")
    price_mode = fields.Selection(
        [("same", "Same price"),
         ("margin", "Source price + margin"),
         ("cost", "Source standard cost")],
        default="margin", required=True)
    margin_percent = fields.Float(
        string="Transfer Margin (%)", default=10.0,
        help="Added to the source price when the policy is a margin.")
    auto_create_po = fields.Boolean(
        string="Create Purchase Order Automatically",
        help="Create the purchase order as soon as the transfer is built.")
    active = fields.Boolean(default=True)
    note = fields.Text()
    mapping_ids = fields.One2many(
        "interco.mapping", "rule_id", string="Product Mappings")

    _sql_constraints = [
        ('company_target_uniq', "unique(company_id, target_company_id)", "A rule already exists between these two companies."),
    ]

    @api.constrains("company_id", "target_company_id")
    def _check_companies(self):
        for rule in self:
            if rule.company_id and rule.target_company_id \
                    and rule.company_id == rule.target_company_id:
                raise ValidationError(_(
                    "The selling company and the buying company must be "
                    "different."))

    def _vendor_partner(self):
        self.ensure_one()
        return self.vendor_partner_id or self.company_id.partner_id

    def _target_price(self, order_line, target_product):
        self.ensure_one()
        if self.price_mode == "cost":
            return target_product.standard_price
        if self.price_mode == "same":
            return order_line.price_unit
        return order_line.price_unit \
            * (1.0 + (self.margin_percent or 0.0) / 100.0)

    def _mapping_for(self, product):
        self.ensure_one()
        return self.mapping_ids.filtered(
            lambda mapping: mapping.source_product_id == product)[:1]

    def action_create_transfer(self):
        self.ensure_one()
        return True

    def _create_transfer(self, order):
        self.ensure_one()
        if order.company_id != self.company_id:
            raise UserError(_(
                "This rule does not apply to the company of the order."))
        if not order.order_line:
            raise UserError(_("The order has no line to transfer."))
        transfer = self.env["interco.transfer"].create({
            "rule_id": self.id,
            "sale_order_id": order.id,
            "company_id": order.company_id.id,
            "target_company_id": self.target_company_id.id,
            "partner_id": order.partner_id.id,
            "vendor_partner_id": self._vendor_partner().id,
        })
        transfer._generate_lines()
        if self.auto_create_po:
            transfer.action_create_purchase()
        return transfer
