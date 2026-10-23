# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RmaRequest(models.Model):
    _name = "rma.request"
    _description = "RMA Return Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="/", copy=False, readonly=True)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    sale_order_id = fields.Many2one("sale.order", string="Sales Order")
    picking_id = fields.Many2one("stock.picking", string="Delivery")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    request_type = fields.Selection(
        [("withdrawal", "Withdrawal 14d"), ("warranty", "Legal Warranty"),
         ("goodwill", "Goodwill")],
        default="withdrawal",
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"), ("submitted", "Submitted"),
            ("approved", "Approved"), ("rejected", "Rejected"),
            ("label_sent", "Label Sent"), ("in_transit", "In Transit"),
            ("received", "Received"), ("qc_done", "QC Done"),
            ("resolved", "Resolved"), ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    reason_id = fields.Many2one("rma.reason", string="Reason", tracking=True)
    resolution = fields.Selection(
        [("refund", "Refund"), ("exchange", "Exchange"),
         ("credit", "Store Credit"), ("refurb", "Refurbish & Resell")],
        tracking=True,
    )
    line_ids = fields.One2many("rma.request.line", "request_id")
    return_picking_ids = fields.One2many("stock.picking", "rma_request_id")
    refund_move_id = fields.Many2one("account.move", string="Credit Note", copy=False)
    exchange_order_id = fields.Many2one("sale.order", string="Exchange Order", copy=False)
    label_pdf_id = fields.Many2one("ir.attachment", string="Return Label", copy=False)
    tracking_ref = fields.Char(string="Carrier Tracking Ref")
    days_since_delivery = fields.Integer(compute="_compute_delivery", store=True)
    amount_to_refund = fields.Float(compute="_compute_amount", store=True)
    return_created = fields.Boolean(copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("rma.request") or "/"
        return super().create(vals_list)

    @api.depends("picking_id")
    def _compute_delivery(self):
        for rec in self:
            if rec.picking_id and rec.picking_id.date_done:
                done = rec.picking_id.date_done.date()
                rec.days_since_delivery = (date.today() - done).days
            else:
                rec.days_since_delivery = 0

    @api.depends("line_ids.subtotal_refund")
    def _compute_amount(self):
        for rec in self:
            rec.amount_to_refund = sum(rec.line_ids.mapped("subtotal_refund"))

    def _window_days(self):
        params = self.env["ir.config_parameter"].sudo()
        if self.request_type == "warranty":
            return int(params.get_str("rma_returns_portal.warranty_days", "730"))
        return int(params.get_str("rma_returns_portal.window_days", "30"))

    def check_eligibility(self):
        self.ensure_one()
        errors = []
        window = self._window_days()
        if self.days_since_delivery > window:
            errors.append(_("Outside the %d-day return window (%d days).")
                          % (window, self.days_since_delivery))
        for line in self.line_ids:
            if not line.product_id.product_tmpl_id.is_returnable:
                errors.append(_("Product %s is flagged non-returnable.")
                              % line.product_id.display_name)
            available = line.qty_delivered - line.qty_already_returned
            if line.qty_requested > available:
                errors.append(_("Requested %s exceeds returnable %s for %s.")
                              % (line.qty_requested, available,
                                 line.product_id.display_name))
        return errors

    def action_submit(self):
        for rec in self:
            errors = rec.check_eligibility()
            if errors:
                raise UserError("\n".join(str(e) for e in errors))
            rec.state = "submitted"
            rec.message_post(body=_("RMA request submitted."))
            auto_amount = float(self.env["ir.config_parameter"].sudo().get_str(
                "rma_returns_portal.auto_amount", "0"))
            if (rec.reason_id.auto_approve and auto_amount
                    and rec.amount_to_refund <= auto_amount):
                rec.action_approve()
                rec.message_post(body=_("Auto-approved under threshold."))

    def action_approve(self):
        for rec in self:
            rec.state = "approved"
            rec._create_return_picking()
            rec.message_post(body=_("RMA approved; return transfer created."))

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_label_sent(self):
        self.write({"state": "label_sent"})

    def action_in_transit(self):
        self.write({"state": "in_transit"})

    def action_receive(self):
        self.write({"state": "received"})

    def _create_return_picking(self):
        for rec in self:
            if rec.return_created or not rec.picking_id:
                continue
            new_picking = rec.picking_id._create_return()
            for move in new_picking.move_ids:
                match = rec.line_ids.filtered(
                    lambda l: l.product_id == move.product_id)
                qty = sum(match.mapped("qty_requested"))
                if qty:
                    move.write({"product_uom_qty": qty})
            new_picking.write({"rma_request_id": rec.id})
            rec.return_created = True

    def action_qc_done(self):
        for rec in self:
            if any(not l.grade_id for l in rec.line_ids):
                raise UserError(_("Set a QC grade on every line before closing QC."))
            rec.state = "qc_done"

    def action_resolve_refund(self):
        for rec in self:
            rec.resolution = "refund"
            invoice = rec.sale_order_id.invoice_ids.filtered(
                lambda m: m.move_type == "out_invoice" and m.state == "posted")[:1]
            if invoice:
                reversal = self.env["account.move.reversal"].with_context(
                    active_model="account.move", active_ids=invoice.ids).create({
                        "reason": _("RMA %s") % rec.name,
                    })
                reversal.reverse_moves()
                credit = self.env["account.move"].search(
                    [("reversed_entry_id", "=", invoice.id)], order="id desc", limit=1)
                rec.refund_move_id = credit.id if credit else False
            rec.state = "resolved"

    def action_resolve_exchange(self):
        for rec in self:
            rec.resolution = "exchange"
            order = rec.sale_order_id.copy({"origin": _("Exchange for %s") % rec.name})
            rec.exchange_order_id = order.id
            rec.state = "resolved"

    def action_resolve_credit(self):
        self.write({"resolution": "credit", "state": "resolved"})

    def action_close(self):
        self.write({"state": "closed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def get_return_label(self, carrier="default"):
        """Hook for carrier connectors: returns label PDF bytes."""
        self.ensure_one()
        return False


class RmaRequestLine(models.Model):
    _name = "rma.request.line"
    _description = "RMA Request Line"

    request_id = fields.Many2one("rma.request", required=True, ondelete="cascade")
    sale_line_id = fields.Many2one("sale.order.line")
    product_id = fields.Many2one("product.product", required=True)
    qty_delivered = fields.Float(default=0.0)
    qty_requested = fields.Float(default=1.0)
    qty_received = fields.Float(default=0.0, copy=False)
    qty_accepted = fields.Float(default=0.0, copy=False)
    qty_already_returned = fields.Float(default=0.0)
    grade_id = fields.Many2one("rma.grade", string="QC Grade")
    disposition = fields.Selection(
        [("restock", "Restock"), ("refurb", "Refurbish"),
         ("scrap", "Scrap"), ("repair", "Repair")])
    price_unit = fields.Float()
    subtotal_refund = fields.Float(compute="_compute_subtotal", store=True)

    @api.depends("qty_requested", "price_unit")
    def _compute_subtotal(self):
        for rec in self:
            fee = rec.request_id.reason_id.restocking_fee_pct or 0.0
            rec.subtotal_refund = rec.qty_requested * rec.price_unit * (1 - fee / 100.0)
