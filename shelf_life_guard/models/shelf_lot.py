# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ShelfLot(models.Model):
    _name = "shelf.lot"
    _description = "Perishable Lot"
    _inherit = ["mail.thread"]
    _order = "expiry_date, id"

    name = fields.Char(
        string="Lot / Reference", required=True, tracking=True)
    product_name = fields.Char(
        string="Product", required=True, tracking=True)
    location_name = fields.Char(
        string="Location", required=True,
        help="Storage location where the lot is currently kept.")
    quantity = fields.Float(
        required=True, default=1.0, digits="Product Unit of Measure")
    received_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    expiry_date = fields.Date(required=True, tracking=True)
    warning_days = fields.Integer(
        default=7, required=True,
        help="Number of days before expiry to consider the lot expiring soon.")
    days_left = fields.Integer(
        compute="_compute_days_left", store=True,
        help="Days remaining until the expiry date.")
    state = fields.Selection(
        [("fresh", "Fresh"), ("expiring", "Expiring Soon"),
         ("expired", "Expired"), ("quarantined", "Quarantined"),
         ("consumed", "Consumed"), ("disposed", "Disposed")],
        default="fresh", required=True, tracking=True, index=True, copy=False)
    is_alert = fields.Boolean(
        compute="_compute_days_left", store=True,
        help="True when the lot is expiring soon or already expired.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()
    active = fields.Boolean(default=True)

    @api.depends("expiry_date", "warning_days", "state")
    def _compute_days_left(self):
        today = fields.Date.context_today(self)
        for lot in self:
            if lot.expiry_date:
                days_left = (lot.expiry_date - today).days
            else:
                days_left = 0
            lot.days_left = days_left
            lot.is_alert = days_left <= lot.warning_days and lot.state in (
                "fresh", "expiring", "expired")

    @api.constrains("received_date", "expiry_date")
    def _check_dates(self):
        for lot in self:
            if lot.expiry_date < lot.received_date:
                raise ValidationError(_(
                    "The expiry date of lot %s cannot come before its "
                    "received date.", lot.name))

    @api.constrains("quantity", "warning_days")
    def _check_values(self):
        for lot in self:
            if lot.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of lot %s must be above zero.", lot.name))
            if lot.warning_days < 0:
                raise ValidationError(_(
                    "The warning window of lot %s cannot be negative.",
                    lot.name))

    def action_refresh_status(self):
        today = fields.Date.context_today(self)
        for lot in self:
            if lot.state in ("consumed", "disposed", "quarantined"):
                continue
            days_left = (lot.expiry_date - today).days if lot.expiry_date else 0
            if days_left < 0:
                lot.state = "expired"
            elif days_left <= lot.warning_days:
                lot.state = "expiring"
            else:
                lot.state = "fresh"
            lot.message_post(body=_("The shelf life status was refreshed."))
        return True

    def action_quarantine(self):
        for lot in self:
            if lot.state in ("consumed", "disposed"):
                raise UserError(_("Consumed or disposed lots cannot be quarantined."))
            lot.state = "quarantined"
            lot.message_post(body=_("The lot was moved to quarantine."))
        return True

    def action_consume(self):
        for lot in self:
            if lot.state in ("consumed", "disposed"):
                raise UserError(_("The lot is already closed."))
            if lot.state == "expired":
                raise UserError(_("Expired lots cannot be consumed."))
            lot.state = "consumed"
            lot.message_post(body=_("The lot was marked as consumed."))
        return True

    def action_dispose(self):
        for lot in self:
            if lot.state in ("consumed", "disposed"):
                raise UserError(_("The lot is already closed."))
            lot.state = "disposed"
            lot.message_post(body=_("The lot was marked as disposed."))
        return True
