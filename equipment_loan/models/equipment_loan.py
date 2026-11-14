# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EquipmentLoanItem(models.Model):
    _name = "equipment.loan.item"
    _description = "Loanable Equipment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name, id"

    name = fields.Char(required=True, tracking=True)
    ref = fields.Char(string="Reference / Serial")
    category = fields.Char(string="Category")
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)
    current_loan_id = fields.Many2one(
        "equipment.loan", string="Current Loan",
        compute="_compute_current_loan")
    is_on_loan = fields.Boolean(
        compute="_compute_current_loan", string="On Loan", store=False)

    def _compute_current_loan(self):
        Loan = self.env["equipment.loan"]
        for rec in self:
            loan = Loan.search([
                ("item_id", "=", rec.id),
                ("state", "=", "ongoing"),
            ], limit=1)
            rec.current_loan_id = loan
            rec.is_on_loan = bool(loan)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "An equipment item with this name already exists for this company."),
    ]


class EquipmentLoan(models.Model):
    _name = "equipment.loan"
    _description = "Equipment Loan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_out desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    item_id = fields.Many2one(
        "equipment.loan.item", string="Equipment", required=True,
        index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True,
        tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    date_out = fields.Date(
        string="Checkout Date", required=True,
        default=fields.Date.context_today, tracking=True)
    date_due = fields.Date(string="Due Date", tracking=True)
    date_return = fields.Date(string="Return Date", readonly=True, copy=False)
    return_condition = fields.Selection(
        [("good", "Good"), ("damaged", "Damaged"), ("lost", "Lost")],
        string="Return Condition", readonly=True, copy=False)
    return_note = fields.Text(string="Return Notes", copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("ongoing", "Ongoing"),
         ("returned", "Returned"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    is_overdue = fields.Boolean(
        compute="_compute_overdue", string="Overdue", store=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("date_due", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = bool(
                rec.state == "ongoing" and rec.date_due and rec.date_due < today)

    @api.constrains("date_out", "date_due")
    def _check_dates(self):
        for rec in self:
            if rec.date_due and rec.date_out and rec.date_due < rec.date_out:
                raise ValidationError(
                    _("The due date cannot be before the checkout date."))

    @api.constrains("item_id", "state")
    def _check_item_available(self):
        for rec in self:
            if rec.state != "ongoing":
                continue
            other = self.search([
                ("id", "!=", rec.id),
                ("item_id", "=", rec.item_id.id),
                ("state", "=", "ongoing"),
            ], limit=1)
            if other:
                raise ValidationError(
                    _("Equipment %(item)s is already on loan (%(loan)s).",
                      item=rec.item_id.display_name, loan=other.name))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("equipment.loan")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Equipment Loan",
                        "code": "equipment.loan",
                        "prefix": "EQL/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_start(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft loan can be started."))
            # re-check availability
            other = self.search([
                ("id", "!=", rec.id),
                ("item_id", "=", rec.item_id.id),
                ("state", "=", "ongoing"),
            ], limit=1)
            if other:
                raise ValidationError(
                    _("Equipment %(item)s is already on loan (%(loan)s).",
                      item=rec.item_id.display_name, loan=other.name))
            rec.state = "ongoing"

    def action_return(self):
        for rec in self:
            if rec.state != "ongoing":
                raise UserError(_("Only an ongoing loan can be returned."))
            rec.write({
                "state": "returned",
                "date_return": fields.Date.context_today(self),
                "return_condition": rec.return_condition or "good",
            })

    def action_cancel(self):
        for rec in self:
            if rec.state in ("ongoing", "returned"):
                raise UserError(_("An ongoing or returned loan cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only a cancelled loan can be reset."))
            rec.write({"state": "draft", "date_return": False,
                       "return_condition": False, "return_note": False})
