# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class WarrantyRegistration(models.Model):
    _name = "warranty.registration"
    _description = "Product Warranty"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, tracking=True)
    serial_number = fields.Char(string="Serial Number", tracking=True, index=True)
    lot_id = fields.Many2one("stock.lot", string="Lot / Serial Record")
    sale_order_id = fields.Many2one("sale.order", string="Sales Order")
    invoice_id = fields.Many2one("account.move", string="Invoice")
    date_start = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    duration_months = fields.Integer(default=12, required=True, tracking=True)
    date_end = fields.Date(
        string="End Date", compute="_compute_date_end", store=True,
        tracking=True)
    is_covered = fields.Boolean(
        string="Covered", compute="_compute_is_covered",
        search="_search_is_covered")
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("void", "Void")],
        default="active", required=True, tracking=True, index=True)
    claim_ids = fields.One2many(
        "warranty.claim", "registration_id", string="Claims")
    claim_count = fields.Integer(compute="_compute_claim_count")
    total_claim_cost = fields.Monetary(
        currency_field="currency_id", compute="_compute_claim_count")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "warranty.registration") or "/"
        return super().create(vals_list)

    @api.constrains("duration_months")
    def _check_duration(self):
        for warranty in self:
            if warranty.duration_months <= 0:
                raise ValidationError(_(
                    "The warranty duration must be at least one month."))

    @api.depends("date_start", "duration_months")
    def _compute_date_end(self):
        for warranty in self:
            if warranty.date_start and warranty.duration_months:
                warranty.date_end = warranty.date_start + relativedelta(
                    months=warranty.duration_months)
            else:
                warranty.date_end = False

    @api.depends("date_end", "state")
    def _compute_is_covered(self):
        today = fields.Date.context_today(self)
        for warranty in self:
            warranty.is_covered = bool(
                warranty.state == "active" and warranty.date_end
                and warranty.date_end >= today)

    def _search_is_covered(self, operator, value):
        today = fields.Date.context_today(self)
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("state", "=", "active"), ("date_end", ">=", today)]
        return ["|", ("state", "!=", "active"), ("date_end", "<", today)]

    @api.depends("claim_ids", "claim_ids.cost")
    def _compute_claim_count(self):
        for warranty in self:
            warranty.claim_count = len(warranty.claim_ids)
            warranty.total_claim_cost = sum(warranty.claim_ids.mapped("cost"))

    def action_expire(self):
        today = fields.Date.context_today(self)
        expired = self.filtered(
            lambda w: w.state == "active" and w.date_end and w.date_end < today)
        expired.write({"state": "expired"})
        return True

    def action_void(self):
        self.write({"state": "void"})

    def action_new_claim(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("New Claim"),
            "res_model": "warranty.claim",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_registration_id": self.id,
                "default_partner_id": self.partner_id.id,
            },
        }

    def action_view_claims(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Claims"),
            "res_model": "warranty.claim",
            "view_mode": "list,form",
            "domain": [("registration_id", "=", self.id)],
            "context": {"default_registration_id": self.id},
        }

    @api.model
    def _cron_expire(self):
        warranties = self.search([("state", "=", "active")])
        return warranties.action_expire()


class WarrantyClaim(models.Model):
    _name = "warranty.claim"
    _description = "Warranty Claim"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    registration_id = fields.Many2one(
        "warranty.registration", string="Warranty", required=True,
        tracking=True, ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        related="registration_id.partner_id", store=True, string="Customer")
    product_id = fields.Many2one(
        related="registration_id.product_id", store=True, string="Product")
    date = fields.Date(
        default=fields.Date.context_today, required=True, tracking=True)
    issue = fields.Text(required=True)
    resolution = fields.Selection(
        [("repair", "Repair"), ("replace", "Replacement"),
         ("refund", "Refund"), ("none", "No Action")],
        default="repair", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"),
         ("done", "Done"), ("refused", "Refused")],
        default="draft", required=True, tracking=True, index=True)
    covered = fields.Boolean(
        string="Covered at Creation", readonly=True)
    goodwill = fields.Boolean(
        string="Goodwill", help="Accept the claim even if not covered.")
    cost = fields.Monetary(
        string="Repair Cost", currency_field="currency_id", tracking=True)
    vendor_recovery = fields.Monetary(
        string="Supplier Recovery", currency_field="currency_id")
    supplier_id = fields.Many2one("res.partner", string="Supplier")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "warranty.claim") or "/"
            registration = self.env["warranty.registration"].browse(
                vals.get("registration_id"))
            if registration:
                vals["covered"] = registration.is_covered
        return super().create(vals_list)

    @api.constrains("cost", "vendor_recovery")
    def _check_amounts(self):
        for claim in self:
            if claim.cost < 0 or claim.vendor_recovery < 0:
                raise ValidationError(_("Amounts cannot be negative."))
            if claim.vendor_recovery > claim.cost:
                raise ValidationError(_(
                    "The supplier recovery cannot exceed the repair cost."))

    def action_approve(self):
        for claim in self:
            if claim.state != "draft":
                raise UserError(_("Only a draft claim can be approved."))
            if not claim.registration_id.is_covered and not claim.goodwill:
                raise UserError(_(
                    "This product is no longer under warranty. "
                    "Tick Goodwill to accept the claim anyway."))
            claim.state = "approved"
        return True

    def action_done(self):
        for claim in self:
            if claim.state != "approved":
                raise UserError(_("Approve the claim before closing it."))
            claim.state = "done"
            claim.message_post(body=_(
                "Claim closed: %(resolution)s, cost %(cost).2f, "
                "supplier recovery %(recovery).2f.",
                resolution=claim.resolution, cost=claim.cost,
                recovery=claim.vendor_recovery))
        return True

    def action_refuse(self):
        self.write({"state": "refused"})

    def action_reset(self):
        self.write({"state": "draft"})


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warranty_ids = fields.One2many(
        "warranty.registration", "sale_order_id", string="Warranties")
    warranty_count = fields.Integer(compute="_compute_warranty_count")

    def _compute_warranty_count(self):
        for order in self:
            order.warranty_count = len(order.warranty_ids)

    def action_view_warranties(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Warranties"),
            "res_model": "warranty.registration",
            "view_mode": "list,form",
            "domain": [("sale_order_id", "=", self.id)],
            "context": {"default_sale_order_id": self.id,
                        "default_partner_id": self.partner_id.id},
        }
