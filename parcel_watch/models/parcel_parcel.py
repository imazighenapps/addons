# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ParcelParcel(models.Model):
    _name = "parcel.parcel"
    _description = "Inbound Parcel"
    _inherit = ["mail.thread"]
    _order = "expected_on, id desc"

    name = fields.Char(
        string="Reference", required=True, copy=False,
        default=lambda self: _("New"), tracking=True)
    tracking_number = fields.Char(required=True, tracking=True)
    carrier = fields.Selection(
        [("dhl", "DHL"), ("fedex", "FedEx"), ("ups", "UPS"),
         ("usps", "USPS"), ("dpd", "DPD"), ("gls", "GLS"),
         ("other", "Other")],
        default="other", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", tracking=True)
    expected_on = fields.Date(string="Expected On", tracking=True)
    received_on = fields.Date(string="Received On", readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("in_transit", "In Transit"),
         ("received", "Received"), ("lost", "Lost")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    tracking_url = fields.Char(
        string="Carrier Link", compute="_compute_tracking_url", store=True)
    is_late = fields.Boolean(
        string="Late", compute="_compute_is_late", store=True, index=True)
    lost_reason = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("carrier", "tracking_number")
    def _compute_tracking_url(self):
        bases = {
            "dhl": "https://www.dhl.com/global-en/home/tracking.html?tracking-id=",
            "fedex": "https://www.fedex.com/fedextrack/?trknbr=",
            "ups": "https://www.ups.com/track?tracknum=",
            "usps": "https://tools.usps.com/go/TrackConfirmAction?tLabels=",
            "dpd": "https://tracking.dpd.de/status/en_US/parcel/",
            "gls": "https://gls-group.eu/track/",
        }
        for parcel in self:
            number = (parcel.tracking_number or "").strip()
            base = bases.get(parcel.carrier)
            parcel.tracking_url = "%s%s" % (base, number) if base and number else False

    @api.depends("expected_on", "state")
    def _compute_is_late(self):
        today = fields.Date.context_today(self)
        for parcel in self:
            parcel.is_late = bool(
                parcel.expected_on
                and parcel.state in ("draft", "in_transit")
                and parcel.expected_on < today)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "parcel.parcel") or _("New")
        return super().create(vals_list)

    # Received dates are set by the receive action; early or late
    # delivery against the expected date is valid. No date constraint.

    def action_mark_in_transit(self):
        for parcel in self:
            if parcel.state != "draft":
                raise ValidationError(_(
                    "Only a draft parcel can be marked in transit."))
            parcel.state = "in_transit"
        return True

    def action_mark_received(self):
        for parcel in self:
            if parcel.state not in ("draft", "in_transit"):
                raise ValidationError(_(
                    "Only a draft or in-transit parcel can be received."))
            parcel.write({
                "state": "received",
                "received_on": fields.Date.context_today(parcel),
            })
            parcel.message_post(body=_("The parcel was received."))
        return True

    def action_mark_lost(self):
        for parcel in self:
            if parcel.state not in ("draft", "in_transit"):
                raise ValidationError(_(
                    "Only a draft or in-transit parcel can be marked lost."))
            parcel.state = "lost"
            parcel.message_post(body=_("The parcel was marked as lost."))
        return True

    def action_reset_draft(self):
        for parcel in self:
            if parcel.state == "received":
                raise ValidationError(_(
                    "A received parcel cannot be reset to draft."))
            parcel.write({"state": "draft", "received_on": False})
        return True
