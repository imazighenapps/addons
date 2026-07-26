from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin_percent = fields.Float(
        string="Margin (%)",
        compute="_compute_margin",
        store=True,
        digits=(16, 2),
    )
    required_margin_percent = fields.Float(
        string="Required Margin (%)",
        compute="_compute_required_margin",
        digits=(16, 2),
        help="Minimum margin required for this order, resolved from the "
             "applicable margin rules (or the default setting).",
    )
    margin_below_threshold = fields.Boolean(
        string="Margin Below Threshold",
        compute="_compute_required_margin",
    )
    margin_block_log_count = fields.Integer(
        string="Margin Log Count",
        compute="_compute_margin_block_log_count",
    )

    @api.depends(
        "order_line.price_subtotal",
        "order_line.product_id.standard_price",
        "order_line.product_uom_qty",
        "order_line.display_type",
        "currency_id",
        "company_id",
        "date_order",
    )
    def _compute_margin(self):
        for order in self:
            company = order.company_id or self.env.company
            company_currency = company.currency_id
            target_currency = order.currency_id or company_currency
            rate_date = order.date_order or fields.Date.context_today(order)

            sale_total = 0.0
            cost_total = 0.0
            for line in order.order_line:
                if line.display_type or not line.product_id:
                    continue
                sale_total += line.price_subtotal
                cost = line.product_id.standard_price * line.product_uom_qty
                if company_currency != target_currency:
                    cost = company_currency._convert(
                        cost, target_currency, company, rate_date
                    )
                cost_total += cost

            margin = sale_total - cost_total
            order.margin_percent = (margin / sale_total) * 100 if sale_total else 0.0

    def _get_min_margin_rule(self):
        """Resolve the minimum margin required for this order.

        Priority: Product/Product Template > Category > Customer > Global
        default. Within a priority level, if several order lines/rules
        match, the STRICTEST (highest) minimum margin wins, so the order
        can never sneak past a rule via a low-cost, unrelated line.
        """
        self.ensure_one()
        Rule = self.env["sale.margin.rule"]
        company = self.company_id or self.env.company
        company_domain = [
            "|", ("company_id", "=", False), ("company_id", "=", company.id)
        ]

        lines = self.order_line.filtered(lambda l: l.product_id and not l.display_type)

        # 1. Product variant, falling back to product template
        if lines:
            product_ids = lines.mapped("product_id").ids
            tmpl_ids = lines.mapped("product_id.product_tmpl_id").ids
            rules = Rule.search(company_domain + [
                ("active", "=", True),
                "|",
                ("product_id", "in", product_ids),
                ("product_tmpl_id", "in", tmpl_ids),
            ])
            if rules:
                return max(rules.mapped("min_margin_percent"))

        # 2. Product category
        if lines:
            categ_ids = lines.mapped("product_id.categ_id").ids
            if categ_ids:
                rules = Rule.search(company_domain + [
                    ("active", "=", True),
                    ("categ_id", "in", categ_ids),
                ])
                if rules:
                    return max(rules.mapped("min_margin_percent"))

        # 3. Customer
        if self.partner_id:
            rules = Rule.search(company_domain + [
                ("active", "=", True),
                ("partner_id", "=", self.partner_id.id),
            ])
            if rules:
                return max(rules.mapped("min_margin_percent"))

        # 4. Global fallback (Settings)
        return float(
            self.env["ir.config_parameter"].sudo().get_param(
                "sale_margin_block_pro.min_margin_percent", 0.0
            )
        )

    @api.depends("margin_percent", "order_line", "partner_id", "company_id")
    def _compute_required_margin(self):
        for order in self:
            required = order._get_min_margin_rule() if order.order_line else 0.0
            order.required_margin_percent = required
            order.margin_below_threshold = order.margin_percent < required

    def _compute_margin_block_log_count(self):
        log_data = self.env["sale.margin.block.log"]._read_group(
            [("order_id", "in", self.ids)], ["order_id"], ["__count"],
        )
        counts = {order.id: count for order, count in log_data}
        for order in self:
            order.margin_block_log_count = counts.get(order.id, 0)

    def _log_margin_event(self, action):
        self.ensure_one()
        self.env["sale.margin.block.log"].sudo().create({
            "order_id": self.id,
            "user_id": self.env.user.id,
            "margin_percent": self.margin_percent,
            "required_margin_percent": self.required_margin_percent,
            "action": action,
        })

    def action_confirm(self):
        can_override = self.env.user.has_group(
            "sale_margin_block_pro.group_margin_manager"
        )
        for order in self:
            if order.margin_below_threshold:
                if not can_override:
                    order._log_margin_event("blocked")
                    raise UserError(_(
                        "Confirmation blocked by margin control.\n\n"
                        "Current margin: %(margin).2f%%\n"
                        "Required minimum: %(required).2f%%\n\n"
                        "Ask a user with margin override rights to confirm "
                        "this order."
                    ) % {
                        "margin": order.margin_percent,
                        "required": order.required_margin_percent,
                    })
                else:
                    order._log_margin_event("overridden")
                    order.message_post(body=_(
                        "Order confirmed below the minimum margin "
                        "threshold (%(margin).2f%% instead of "
                        "%(required).2f%%) by %(user)s."
                    ) % {
                        "margin": order.margin_percent,
                        "required": order.required_margin_percent,
                        "user": self.env.user.name,
                    })
        return super().action_confirm()

    def action_view_margin_block_logs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Margin Block / Override Log"),
            "res_model": "sale.margin.block.log",
            "view_mode": "list,form",
            "domain": [("order_id", "=", self.id)],
        }
