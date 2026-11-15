# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ShipmentDelayAlert(models.Model):
    _name = "shipment.delay.alert"
    _description = "Shipment Delay Alert"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "delay_days desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    picking_id = fields.Many2one(
        "stock.picking", string="Transfer", required=True, index=True,
        ondelete="cascade", tracking=True)
    sale_id = fields.Many2one(
        "sale.order", string="Sales Order", index=True, ondelete="set null")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", index=True, tracking=True)
    expected_date = fields.Datetime(string="Scheduled")
    delay_days = fields.Integer(string="Delay (days)", index=True)
    state = fields.Selection(
        [("open", "Open"), ("contacted", "Contacted"),
         ("resolved", "Resolved"), ("dismissed", "Dismissed")],
        default="open", required=True, tracking=True, index=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible",
        default=lambda self: self.env.user)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code(
                    "shipment.delay.alert")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Shipment Delay Alert",
                        "code": "shipment.delay.alert",
                        "prefix": "DLY/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_contacted(self):
        for alert in self:
            if alert.state != "open":
                raise UserError(_("Only an open alert can be marked contacted."))
            alert.state = "contacted"
            alert.message_post(body=_(
                "Customer contacted about late transfer %s.",
                alert.picking_id.name or ""))
        return True

    def action_resolve(self):
        for alert in self:
            if alert.state in ("resolved", "dismissed"):
                raise UserError(_("This alert is already closed."))
            alert.state = "resolved"
        return True

    def action_dismiss(self):
        for alert in self:
            if alert.state in ("resolved", "dismissed"):
                raise UserError(_("This alert is already closed."))
            alert.state = "dismissed"
        return True

    def action_reopen(self):
        for alert in self:
            if alert.state not in ("resolved", "dismissed"):
                raise UserError(_("Only a closed alert can be reopened."))
            alert.state = "open"
        return True


class ShipmentDelayScan(models.TransientModel):
    _name = "shipment.delay.scan"
    _description = "Scan Late Shipments"

    as_of = fields.Datetime(
        string="As Of", required=True, default=fields.Datetime.now)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)

    def action_scan(self):
        self.ensure_one()
        Picking = self.env["stock.picking"]
        Alert = self.env["shipment.delay.alert"]
        domain = [
            ("company_id", "=", self.company_id.id),
            ("picking_type_code", "=", "outgoing"),
            ("state", "not in", ("done", "cancel")),
            ("scheduled_date", "!=", False),
            ("scheduled_date", "<", self.as_of),
        ]
        already = Alert.search([
            ("state", "=", "open"),
        ]).mapped("picking_id")
        pickings = Picking.search(domain) - already
        created = Alert
        for picking in pickings:
            scheduled = picking.scheduled_date
            delay = max(0, (self.as_of.date() - scheduled.date()).days)
            sale = picking.sale_id if "sale_id" in picking._fields else False
            created |= Alert.create({
                "picking_id": picking.id,
                "sale_id": sale.id if sale else False,
                "partner_id": (sale.partner_id.id if sale
                               else picking.partner_id.id),
                "expected_date": scheduled,
                "delay_days": delay,
                "company_id": self.company_id.id,
            })
        action = self.env["ir.actions.actions"]._for_xml_id(
            "shipment_delay_alert.action_shipment_delay_alert")
        if created:
            action["domain"] = [("id", "in", created.ids)]
        return action
