# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VendorReview(models.Model):
    _name = "vendor.review"
    _description = "Supplier Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, partner_id"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, tracking=True,
        domain=[("supplier_rank", ">", 0)])
    period_start = fields.Date(
        required=True, tracking=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1))
    period_end = fields.Date(
        required=True, tracking=True, default=fields.Date.context_today)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    order_count = fields.Integer(readonly=True)
    on_time_rate = fields.Float(
        string="On-Time Delivery (%)", readonly=True)
    fill_rate = fields.Float(
        string="Fill Rate (%)", readonly=True)
    price_variance = fields.Float(
        string="Price Variance (%)", readonly=True)
    quality_rate = fields.Float(
        string="Quality Rate (%)", default=100.0, tracking=True,
        help="Percentage of received goods without a quality issue.")
    score = fields.Float(compute="_compute_score", store=True, tracking=True)
    rating = fields.Selection(
        [("a", "A - Strategic"), ("b", "B - Reliable"),
         ("c", "C - To Improve"), ("d", "D - At Risk")],
        compute="_compute_score", store=True, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated")],
        default="draft", required=True, tracking=True)
    validated_on = fields.Datetime(readonly=True)
    action_ids = fields.One2many(
        "vendor.action", "review_id", string="Improvement Plan")
    action_count = fields.Integer(compute="_compute_action_count")
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "vendor.review") or "/"
        return super().create(vals_list)

    @api.constrains("period_start", "period_end", "quality_rate")
    def _check_values(self):
        for review in self:
            if review.period_end < review.period_start:
                raise UserError(_("The end date must be after the start date."))
            if not 0 <= review.quality_rate <= 100:
                raise UserError(_("The quality rate must be between 0 and 100."))

    @api.depends("on_time_rate", "fill_rate", "price_variance", "quality_rate")
    def _compute_score(self):
        for review in self:
            price_component = max(0.0, 100.0 - min(review.price_variance, 100.0))
            review.score = (
                review.on_time_rate * 0.40
                + review.fill_rate * 0.30
                + review.quality_rate * 0.20
                + price_component * 0.10
            )
            if review.score >= 85:
                review.rating = "a"
            elif review.score >= 70:
                review.rating = "b"
            elif review.score >= 50:
                review.rating = "c"
            else:
                review.rating = "d"

    @api.depends("action_ids")
    def _compute_action_count(self):
        for review in self:
            review.action_count = len(review.action_ids)

    def action_compute(self):
        for review in self:
            orders = self.env["purchase.order"].search([
                ("partner_id", "=", review.partner_id.id),
                ("company_id", "=", review.company_id.id),
                ("state", "in", ["purchase", "done"]),
                ("date_approve", ">=", review.period_start),
                ("date_approve", "<=", review.period_end),
            ])
            review.order_count = len(orders)
            on_time = 0
            measured = 0
            for order in orders:
                if order.effective_date and order.date_planned:
                    measured += 1
                    if order.effective_date <= order.date_planned:
                        on_time += 1
            review.on_time_rate = (on_time / measured * 100.0) if measured \
                else 100.0
            lines = orders.mapped("order_line")
            ordered = sum(lines.mapped("product_qty"))
            received = sum(lines.mapped("qty_received"))
            review.fill_rate = (received / ordered * 100.0) if ordered else 100.0
            variances = []
            for line in lines:
                standard = line.product_id.standard_price
                if standard:
                    variances.append(
                        abs(line.price_unit - standard) / standard * 100.0)
            review.price_variance = (
                sum(variances) / len(variances)) if variances else 0.0
            review._compute_score()
        return True

    def action_validate(self):
        for review in self:
            if review.state != "draft":
                raise UserError(_("This review is already validated."))
            if not review.action_ids and review.rating in ("c", "d"):
                raise UserError(_(
                    "Add an improvement action before validating a "
                    "C or D supplier."))
            review.write({
                "state": "validated",
                "validated_on": fields.Datetime.now(),
            })
            review.message_post(body=_(
                "Review validated with a score of %.1f (%s).",
                review.score, dict(review._fields["rating"].selection)[
                    review.rating]))
        return True

    def action_reset(self):
        self.write({"state": "draft", "validated_on": False})


class VendorAction(models.Model):
    _name = "vendor.action"
    _description = "Supplier Improvement Action"
    _order = "deadline, id"

    review_id = fields.Many2one(
        "vendor.review", required=True, ondelete="cascade", index=True)
    name = fields.Char(string="Action", required=True)
    user_id = fields.Many2one(
        "res.users", string="Owner",
        default=lambda self: self.env.user, required=True)
    deadline = fields.Date(
        default=lambda self: fields.Date.context_today(self))
    done = fields.Boolean(default=False)
    result = fields.Text()
    company_id = fields.Many2one(
        related="review_id.company_id", store=True, readonly=True)


class ResPartner(models.Model):
    _inherit = "res.partner"

    vendor_review_ids = fields.One2many(
        "vendor.review", "partner_id", string="Supplier Reviews")
    vendor_score = fields.Float(
        string="Last Score", compute="_compute_vendor_score")
    vendor_rating = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
        compute="_compute_vendor_score", string="Last Rating")

    def _compute_vendor_score(self):
        for partner in self:
            review = self.env["vendor.review"].search(
                [("partner_id", "=", partner.id)], limit=1,
                order="period_end desc, id desc")
            partner.vendor_score = review.score if review else 0.0
            partner.vendor_rating = review.rating if review else False
