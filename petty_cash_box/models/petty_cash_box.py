# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class PettyCashCategory(models.Model):
    _name = "petty.cash.category"
    _description = "Petty Cash Category"
    _order = "name, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "A category with this name already exists for this company.")


class PettyCashBox(models.Model):
    _name = "petty.cash.box"
    _description = "Petty Cash Box"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name, id"

    name = fields.Char(required=True, tracking=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    opening_balance = fields.Monetary(
        string="Opening Balance", currency_field="currency_id",
        default=0.0, tracking=True)
    balance = fields.Monetary(
        compute="_compute_balance", currency_field="currency_id",
        string="Current Balance", store=True)
    movement_ids = fields.One2many(
        "petty.cash.movement", "box_id", string="Movements")
    count_ids = fields.One2many(
        "petty.cash.count", "box_id", string="Counts")
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("opening_balance", "movement_ids.amount",
                 "movement_ids.movement_type", "movement_ids.state")
    def _compute_balance(self):
        for rec in self:
            balance = rec.opening_balance or 0.0
            for mv in rec.movement_ids.filtered(lambda m: m.state == "posted"):
                if mv.movement_type == "in":
                    balance += mv.amount
                else:
                    balance -= mv.amount
            rec.balance = balance

    @api.constrains("opening_balance")
    def _check_opening(self):
        for rec in self:
            if rec.opening_balance < -EPS:
                raise ValidationError(
                    _("The opening balance cannot be negative."))


class PettyCashMovement(models.Model):
    _name = "petty.cash.movement"
    _description = "Petty Cash Movement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    box_id = fields.Many2one(
        "petty.cash.box", string="Box", required=True, index=True,
        tracking=True, ondelete="cascade")
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    movement_type = fields.Selection(
        [("in", "Top-up"), ("out", "Expense"), ("adjust", "Adjustment")],
        string="Type", required=True, default="out", tracking=True)
    category_id = fields.Many2one(
        "petty.cash.category", string="Category")
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", required=True,
        tracking=True)
    currency_id = fields.Many2one(
        related="box_id.currency_id", store=True, readonly=True)
    partner_ref = fields.Char(string="Paid To / Reference")
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        related="box_id.company_id", store=True, readonly=True)

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(
                    _("The movement amount must be strictly positive."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("petty.cash.movement")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Petty Cash Movement",
                        "code": "petty.cash.movement",
                        "prefix": "PCM/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_post(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft movement can be posted."))
            rec.state = "posted"

    def action_cancel(self):
        for rec in self:
            if rec.state == "cancelled":
                continue
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only a cancelled movement can be reset."))
            rec.state = "draft"


class PettyCashCount(models.Model):
    _name = "petty.cash.count"
    _description = "Petty Cash Count"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    box_id = fields.Many2one(
        "petty.cash.box", string="Box", required=True, index=True,
        tracking=True, ondelete="cascade")
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    currency_id = fields.Many2one(
        related="box_id.currency_id", store=True, readonly=True)
    expected_amount = fields.Monetary(
        string="Expected Amount", currency_field="currency_id",
        compute="_compute_expected", store=True)
    counted_amount = fields.Monetary(
        string="Counted Amount", currency_field="currency_id",
        required=True, tracking=True)
    difference = fields.Monetary(
        compute="_compute_difference", currency_field="currency_id",
        string="Difference", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        default="draft", required=True, tracking=True)
    note = fields.Text()
    company_id = fields.Many2one(
        related="box_id.company_id", store=True, readonly=True)

    @api.depends("box_id", "box_id.balance")
    def _compute_expected(self):
        for rec in self:
            rec.expected_amount = rec.box_id.balance if rec.box_id else 0.0

    @api.depends("expected_amount", "counted_amount")
    def _compute_difference(self):
        for rec in self:
            rec.difference = rec.counted_amount - rec.expected_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("petty.cash.count")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Petty Cash Count",
                        "code": "petty.cash.count",
                        "prefix": "PCC/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_done(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft count can be confirmed."))
            # snapshot expected at confirmation time
            rec.expected_amount = rec.box_id.balance
            rec.state = "done"
