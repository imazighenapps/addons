# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BackorderCase(models.Model):
    _name = "backorder.case"
    _description = "Backorder Case"
    _inherit = ["mail.thread"]
    _order = "promised_date asc, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        index=True)
    product_name = fields.Char(
        string="Product", required=True,
        help="Product or description of the backordered item.")
    ordered_qty = fields.Float(
        string="Ordered Qty", required=True, default=1.0,
        help="Quantity originally ordered by the customer.")
    missing_qty = fields.Float(
        string="Missing Qty", required=True, default=1.0,
        help="Quantity still short and waiting to be fulfilled.")
    promised_date = fields.Date(
        string="Promised Date", required=True, tracking=True)
    customer_message = fields.Text(
        string="Customer Message",
        help="Latest message ready to share with the customer.")
    update_ids = fields.One2many(
        "backorder.update", "case_id", string="Updates")
    update_count = fields.Integer(
        string="Updates", compute="_compute_update_count", store=True)
    is_late = fields.Boolean(
        string="Late", compute="_compute_is_late", store=True, index=True,
        help="True when the promised date has passed and the case is open.")
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")],
        default="open", required=True, tracking=True, index=True)
    resolved_on = fields.Date(string="Resolved On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("update_ids")
    def _compute_update_count(self):
        for case in self:
            case.update_count = len(case.update_ids)

    @api.depends("promised_date", "state")
    def _compute_is_late(self):
        today = fields.Date.context_today(self)
        for case in self:
            case.is_late = bool(
                case.state == "open" and case.promised_date
                and case.promised_date < today)

    @api.constrains("ordered_qty", "missing_qty")
    def _check_quantities(self):
        for case in self:
            if case.ordered_qty <= 0:
                raise ValidationError(_(
                    "The ordered quantity of %s must be above zero.",
                    case.name))
            if case.missing_qty <= 0:
                raise ValidationError(_(
                    "The missing quantity of %s must be above zero.",
                    case.name))
            if case.missing_qty > case.ordered_qty:
                raise ValidationError(_(
                    "The missing quantity of %s cannot exceed the ordered "
                    "quantity.", case.name))

    def action_resolve(self):
        for case in self:
            if case.state != "open":
                raise ValidationError(_(
                    "The backorder case %s is already resolved.", case.name))
            case.write({
                "state": "resolved",
                "resolved_on": fields.Date.context_today(case),
            })
            case.message_post(body=_("The shortage has been resolved."))
        return True

    def action_reopen(self):
        for case in self:
            if case.state != "resolved":
                raise ValidationError(_(
                    "Only resolved backorder cases can be reopened."))
            case.write({"state": "open", "resolved_on": False})
            case.message_post(body=_("The backorder case has been reopened."))
        return True
