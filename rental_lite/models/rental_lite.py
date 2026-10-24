# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_rental = fields.Boolean(string="Rentable", help="Can be rented by the day.")
    rental_price = fields.Monetary(
        string="Daily Rental Price", currency_field="currency_id")
    rental_stock = fields.Integer(
        string="Owned Units", default=1,
        help="Number of units available for rental.")
    rental_deposit = fields.Monetary(
        string="Default Deposit", currency_field="currency_id")


class RentalContract(models.Model):
    _name = "rental.contract"
    _description = "Rental Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True)
    date_start = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    return_date = fields.Date(tracking=True)
    line_ids = fields.One2many(
        "rental.contract.line", "contract_id", string="Equipment")
    day_count = fields.Integer(compute="_compute_totals", store=True)
    rental_total = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    deposit_amount = fields.Monetary(currency_field="currency_id", tracking=True)
    damage_fee = fields.Monetary(currency_field="currency_id", tracking=True)
    deposit_refund = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    total_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("picked_up", "Picked Up"), ("returned", "Returned"),
         ("invoiced", "Invoiced"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    return_condition = fields.Selection(
        [("good", "Good"), ("damaged", "Damaged"), ("lost", "Lost")],
        default="good", tracking=True)
    invoice_id = fields.Many2one("account.move", string="Invoice", readonly=True)
    is_overdue = fields.Boolean(
        compute="_compute_totals", search="_search_is_overdue")
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "rental.contract") or "/"
        return super().create(vals_list)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for contract in self:
            if contract.date_end < contract.date_start:
                raise ValidationError(
                    _("The end date must be after the start date."))

    @api.depends("date_start", "date_end", "line_ids.subtotal",
                 "deposit_amount", "damage_fee")
    def _compute_totals(self):
        today = fields.Date.context_today(self)
        for contract in self:
            days = 0
            if contract.date_start and contract.date_end:
                days = (contract.date_end - contract.date_start).days + 1
            contract.day_count = days
            contract.rental_total = sum(contract.line_ids.mapped("subtotal"))
            contract.deposit_refund = (contract.deposit_amount or 0.0) \
                - (contract.damage_fee or 0.0)
            contract.total_amount = contract.rental_total \
                + (contract.deposit_amount or 0.0)
            contract.is_overdue = bool(
                contract.state == "picked_up" and contract.date_end
                and contract.date_end < today)

    def _check_availability(self):
        self.ensure_one()
        for line in self.line_ids:
            product = line.product_id
            if not product.is_rental:
                raise UserError(_(
                    "%s is not marked as rentable.", product.display_name))
            overlapping = self.env["rental.contract.line"].search([
                ("product_id", "=", product.id),
                ("contract_id.state", "in", ["confirmed", "picked_up"]),
                ("contract_id.date_start", "<=", self.date_end),
                ("contract_id.date_end", ">=", self.date_start),
                ("contract_id", "!=", self.id),
            ])
            booked = sum(overlapping.mapped("quantity"))
            owned = product.rental_stock or 0
            if booked + line.quantity > owned:
                raise UserError(_(
                    "%(product)s is not available on this period: "
                    "%(booked)s already booked, %(owned)s owned.",
                    product=product.display_name, booked=booked, owned=owned))

    def action_confirm(self):
        for contract in self:
            if contract.state != "draft":
                raise UserError(_("Only a draft contract can be confirmed."))
            if not contract.line_ids:
                raise UserError(_("Add at least one equipment line."))
            contract._check_availability()
            contract.state = "confirmed"
        return True

    def action_pickup(self):
        for contract in self:
            if contract.state != "confirmed":
                raise UserError(_("Confirm the contract first."))
            contract.state = "picked_up"
        return True

    def action_return(self):
        for contract in self:
            if contract.state != "picked_up":
                raise UserError(_("Only a picked-up contract can be returned."))
            contract.return_date = fields.Date.context_today(contract)
            if contract.return_condition == "lost":
                contract.damage_fee = contract.deposit_amount
            contract.state = "returned"
        return True

    def action_cancel(self):
        for contract in self:
            if contract.state == "invoiced":
                raise UserError(_("An invoiced contract cannot be cancelled."))
            contract.state = "cancelled"
        return True

    def action_invoice(self):
        for contract in self:
            if contract.state not in ("returned", "confirmed", "picked_up"):
                raise UserError(_(
                    "Confirm or return the contract before invoicing it."))
            if contract.invoice_id:
                raise UserError(_("This contract is already invoiced."))
            journal = self.env["account.journal"].search([
                ("type", "=", "sale"),
                ("company_id", "=", contract.company_id.id),
            ], limit=1)
            if not journal:
                raise UserError(_("No sales journal found."))
            lines = []
            for line in contract.line_ids:
                lines.append((0, 0, {
                    "product_id": line.product_id.id,
                    "name": _("%(product)s - %(days)s day(s) from %(start)s",
                              product=line.product_id.display_name,
                              days=contract.day_count,
                              start=contract.date_start),
                    "quantity": line.quantity * contract.day_count,
                    "price_unit": line.unit_price,
                    "tax_ids": [(5, 0, 0)],
                }))
            if contract.deposit_amount:
                lines.append((0, 0, {
                    "name": _("Refundable deposit"),
                    "quantity": 1,
                    "price_unit": contract.deposit_amount,
                    "tax_ids": [(5, 0, 0)],
                }))
            invoice = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": contract.partner_id.id,
                "journal_id": journal.id,
                "invoice_date": fields.Date.context_today(contract),
                "invoice_line_ids": lines,
            })
            contract.write({"invoice_id": invoice.id, "state": "invoiced"})
            contract.message_post(body=_("Invoice %s created.", invoice.name))
        return True

    def action_view_invoice(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoice"),
            "res_model": "account.move",
            "res_id": self.invoice_id.id,
            "view_mode": "form",
        }

    def _search_is_overdue(self, operator, value):
        today = fields.Date.context_today(self)
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("state", "=", "picked_up"), ("date_end", "<", today)]
        return ["|", ("state", "!=", "picked_up"), ("date_end", ">=", today)]


class RentalContractLine(models.Model):
    _name = "rental.contract.line"
    _description = "Rental Contract Line"
    _order = "contract_id, sequence, id"

    contract_id = fields.Many2one(
        "rental.contract", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product", string="Equipment", required=True,
        domain=[("is_rental", "=", True)])
    description = fields.Char()
    quantity = fields.Float(default=1.0, required=True)
    unit_price = fields.Monetary(
        string="Daily Price", currency_field="currency_id")
    subtotal = fields.Monetary(
        currency_field="currency_id", compute="_compute_subtotal", store=True)
    currency_id = fields.Many2one(
        related="contract_id.currency_id", store=True, readonly=True)

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.product_id:
            self.unit_price = self.product_id.rental_price
            self.description = self.product_id.display_name

    @api.depends("quantity", "unit_price", "contract_id.day_count")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price \
                * (line.contract_id.day_count or 1)

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("The quantity must be positive."))
