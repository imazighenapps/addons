from odoo import models, fields


class SaleMarginBlockLog(models.Model):
    _name = "sale.margin.block.log"
    _description = "Sale Margin Block / Override Log"
    _order = "create_date desc"
    _rec_name = "order_id"

    order_id = fields.Many2one(
        "sale.order", string="Sales Order", required=True,
        ondelete="cascade", index=True,
    )
    partner_id = fields.Many2one(
        related="order_id.partner_id", string="Customer", store=True,
    )
    user_id = fields.Many2one(
        "res.users", string="User", required=True, default=lambda self: self.env.user,
    )
    margin_percent = fields.Float(string="Margin (%)", digits=(16, 2))
    required_margin_percent = fields.Float(
        string="Required Margin (%)", digits=(16, 2),
    )
    action = fields.Selection(
        [
            ("blocked", "Blocked"),
            ("overridden", "Overridden"),
        ],
        string="Action",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company", related="order_id.company_id", store=True,
    )
