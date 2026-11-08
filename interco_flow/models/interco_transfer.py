# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IntercoTransfer(models.Model):
    _name = "interco.transfer"
    _description = "Intercompany Transfer"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    rule_id = fields.Many2one("interco.rule", string="Rule", required=True)
    sale_order_id = fields.Many2one(
        "sale.order", string="Sales Order", required=True,
        ondelete="cascade")
    purchase_order_id = fields.Many2one(
        "purchase.order", string="Purchase Order", readonly=True,
        copy=False)
    partner_id = fields.Many2one(
        related="sale_order_id.partner_id", store=True, readonly=True)
    vendor_partner_id = fields.Many2one(
        "res.partner", string="Vendor Partner")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    target_company_id = fields.Many2one(
        "res.company", string="Buying Company", required=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    line_ids = fields.One2many(
        "interco.transfer.line", "transfer_id", string="Lines")
    amount_sale = fields.Monetary(
        string="Sale Amount", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    amount_purchase = fields.Monetary(
        string="Purchase Amount", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    margin_amount = fields.Monetary(
        string="Margin", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    margin_rate = fields.Float(
        string="Margin (%)", compute="_compute_amounts", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("created", "Purchase Created"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()

    _sale_order_uniq = models.Constraint(
        "unique(sale_order_id)",
        "An intercompany transfer already exists for this sales order.")

    @api.depends("sale_order_id", "target_company_id")
    def _compute_name(self):
        for transfer in self:
            transfer.name = "%s / %s" % (
                transfer.sale_order_id.name or _("Transfer"),
                transfer.target_company_id.name or "") \
                if transfer.sale_order_id else _("Intercompany Transfer")

    @api.depends("line_ids.subtotal", "line_ids.subtotal_sale")
    def _compute_amounts(self):
        for transfer in self:
            sale = sum(transfer.line_ids.mapped("subtotal_sale"))
            purchase = sum(transfer.line_ids.mapped("subtotal"))
            transfer.amount_sale = sale
            transfer.amount_purchase = purchase
            transfer.margin_amount = sale - purchase
            transfer.margin_rate = (sale - purchase) / sale * 100.0 \
                if sale else 0.0

    def _generate_lines(self):
        self.ensure_one()
        self.line_ids.unlink()
        Line = self.env["interco.transfer.line"]
        for order_line in self.sale_order_id.order_line:
            if order_line.display_type or not order_line.product_id:
                continue
            mapping = self.rule_id._mapping_for(order_line.product_id)
            target = mapping.target_product_id if mapping \
                else order_line.product_id
            price = mapping.price_unit if mapping and mapping.price_unit \
                else self.rule_id._target_price(order_line, target)
            Line.create({
                "transfer_id": self.id,
                "source_product_id": order_line.product_id.id,
                "target_product_id": target.id,
                "product_qty": order_line.product_uom_qty,
                "price_unit": price,
                "subtotal_sale": order_line.price_subtotal,
            })
        return True

    def action_create_purchase(self):
        self.ensure_one()
        if self.purchase_order_id:
            return self.action_open_purchase()
        if not self.line_ids:
            raise UserError(_("The transfer has no line to purchase."))
        if not self.vendor_partner_id:
            raise UserError(_("A vendor partner is required to buy."))
        # 20.0 renamed product_uom to product_uom_id and then to uom_id.
        pol_fields = self.env["purchase.order.line"]._fields
        uom_key = next(
            (name for name in ("uom_id", "product_uom_id", "product_uom")
             if name in pol_fields), "product_uom")

        def line_values(line):
            values = {
                "product_id": line.target_product_id.id,
                "name": line.target_product_id.display_name,
                "product_qty": line.product_qty,
                "price_unit": line.price_unit,
                "date_planned": fields.Datetime.now(),
            }
            values[uom_key] = line.target_product_id.uom_id.id
            return values

        order = self.env["purchase.order"].with_company(
            self.target_company_id).create({
                "partner_id": self.vendor_partner_id.id,
                "origin": self.sale_order_id.name or self.name,
                "company_id": self.target_company_id.id,
                "order_line": [(0, 0, line_values(line))
                               for line in self.line_ids],
            })
        self.write({"purchase_order_id": order.id, "state": "created"})
        self.message_post(body=_("Purchase order %s created in %s.")
                          % (order.name, self.target_company_id.name))
        return self.action_open_purchase()

    def action_open_purchase(self):
        self.ensure_one()
        if not self.purchase_order_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Purchase Order"),
            "res_model": "purchase.order",
            "view_mode": "form",
            "res_id": self.purchase_order_id.id,
        }

    def action_cancel(self):
        for transfer in self:
            transfer.state = "cancelled"
        return True
