# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class ReturnFlowReason(models.Model):
    _name = "return.flow.reason"
    _description = "Return Motive"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "A return motive with this name already exists for this company.")


class ReturnFlowRequest(models.Model):
    _name = "return.flow.request"
    _description = "Customer Return"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    picking_id = fields.Many2one(
        "stock.picking", string="Delivery", required=True, index=True,
        tracking=True,
        domain="[('picking_type_code', '=', 'outgoing'),"
               " ('state', '=', 'done')]",
        help="The validated outgoing delivery this return comes from.")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True,
        tracking=True)
    reason_id = fields.Many2one(
        "return.flow.reason", string="Return Motive", required=True,
        tracking=True)
    state = fields.Selection(
        [("requested", "Requested"), ("received", "Received"),
         ("inspected", "Inspected"), ("restocked", "Restocked"),
         ("repaired", "Repaired"), ("scrapped", "Scrapped"),
         ("cancelled", "Cancelled")],
        default="requested", required=True, tracking=True, index=True,
        copy=False)
    outcome = fields.Selection(
        [("restock", "Restock"), ("repair", "Repair"), ("scrap", "Scrap")],
        tracking=True, copy=False,
        help="Physical outcome decided at inspection.")
    date_requested = fields.Date(
        default=fields.Date.context_today, required=True)
    date_received = fields.Date(readonly=True, copy=False)
    date_inspected = fields.Date(readonly=True, copy=False)
    line_ids = fields.One2many(
        "return.flow.line", "request_id", string="Return Lines", copy=True)
    total_qty = fields.Float(
        compute="_compute_totals", string="Returned Quantity", store=True)
    credit_move_id = fields.Many2one(
        "account.move", string="Credit Note", readonly=True, copy=False)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("line_ids.qty")
    def _compute_totals(self):
        for rec in self:
            rec.total_qty = sum(rec.line_ids.mapped("qty"))

    @api.constrains("line_ids")
    def _check_lines(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_(
                    "A return must contain at least one line."))

    @api.onchange("picking_id")
    def _onchange_picking(self):
        if self.picking_id:
            self.partner_id = self.picking_id.partner_id
            self.company_id = self.picking_id.company_id
            lines = [(5, 0, 0)]
            for move in self.picking_id.move_ids.filtered(
                    lambda m: m.state == "done"):
                qty = move.quantity if "quantity" in move._fields \
                    else move.product_uom_qty
                if qty <= 0:
                    continue
                line_vals = {
                    "move_id": move.id,
                    "product_id": move.product_id.id,
                    "qty_delivered": qty,
                    "qty": qty,
                    "product_uom": move.product_uom.id,
                }
                lines.append((0, 0, line_vals))
            self.line_ids = lines

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code(
                    "return.flow.request")
                vals["name"] = seq or self.env["ir.sequence"].next_by_code(
                    "return.flow") or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Customer Return",
                        "code": "return.flow.request",
                        "prefix": "RET/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def _ensure_lines(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add at least one return line."))

    def action_receive(self):
        for rec in self:
            if rec.state != "requested":
                raise UserError(_("Only a requested return can be received."))
            rec._ensure_lines()
            rec.write({"state": "received",
                       "date_received": fields.Date.context_today(self)})

    def action_inspect(self):
        for rec in self:
            if rec.state != "received":
                raise UserError(_("Only a received return can be inspected."))
            rec.write({"state": "inspected",
                       "date_inspected": fields.Date.context_today(self)})

    def _apply_outcome(self, outcome):
        self.ensure_one()
        if self.state != "inspected":
            raise UserError(_("Decide the outcome after inspection."))
        self.write({"state": {"restock": "restocked",
                              "repair": "repaired",
                              "scrap": "scrapped"}[outcome],
                    "outcome": outcome})

    def action_restock(self):
        for rec in self:
            rec._apply_outcome("restock")
            rec._create_restock_move()

    def action_repair(self):
        for rec in self:
            rec._apply_outcome("repair")

    def action_scrap(self):
        for rec in self:
            rec._apply_outcome("scrap")

    def _create_restock_move(self):
        self.ensure_one()
        picking_type = self.env["stock.picking.type"].search([
            ("code", "=", "incoming"),
            ("warehouse_id.company_id", "=", self.company_id.id),
        ], limit=1)
        if not picking_type:
            picking_type = self.env["stock.picking.type"].search([
                ("code", "=", "incoming")], limit=1)
        if not picking_type:
            return
        dest = self.picking_id.location_dest_id
        src = self.picking_id.location_id
        move_vals = []
        for line in self.line_ids:
            if line.qty <= 0:
                continue
            vals = {
                "product_id": line.product_id.id,
                "product_uom_qty": line.qty,
                "location_id": src.id,
                "location_dest_id": dest.id,
            }
            if "name" in self.env["stock.move"]._fields:
                vals["name"] = line.product_id.display_name or self.name
            if "product_uom" in self.env["stock.move"]._fields:
                vals["product_uom"] = line.uom_id.id
            move_vals.append((0, 0, vals))
        if not move_vals:
            return
        picking = self.env["stock.picking"].create({
            "picking_type_id": picking_type.id,
            "partner_id": self.partner_id.id,
            "origin": self.name,
            "location_id": src.id,
            "location_dest_id": dest.id,
            "company_id": self.company_id.id,
            "move_ids": move_vals,
        })
        picking.action_confirm()
        for move in picking.move_ids:
            if "quantity" in move._fields:
                move.quantity = move.product_uom_qty
            elif "quantity_done" in move._fields:
                move.quantity_done = move.product_uom_qty
        try:
            picking.button_validate()
        except Exception:
            pass

    def action_create_credit_note(self):
        self.ensure_one()
        if self.state not in ("inspected", "restocked", "repaired",
                              "scrapped"):
            raise UserError(_(
                "Inspect the return before creating a credit note."))
        if self.credit_move_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.move",
                "res_id": self.credit_move_id.id,
                "view_mode": "form",
            }
        move_type = "out_refund"
        journal = self.env["account.journal"].search([
            ("type", "=", "sale"), ("company_id", "=", self.company_id.id),
        ], limit=1)
        invoice_lines = []
        for line in self.line_ids:
            if line.qty <= 0:
                continue
            vals = {
                "product_id": line.product_id.id,
                "quantity": line.qty,
                "name": line.product_id.display_name or self.name,
            }
            if line.uom_id:
                vals["product_uom_id"] = line.uom_id.id
            invoice_lines.append((0, 0, vals))
        if not invoice_lines:
            raise UserError(_("There is no quantity to refund."))
        move_vals = {
            "move_type": move_type,
            "partner_id": self.partner_id.id,
            "invoice_origin": self.name,
            "company_id": self.company_id.id,
            "invoice_line_ids": invoice_lines,
        }
        if journal:
            move_vals["journal_id"] = journal.id
        move = self.env["account.move"].create(move_vals)
        self.credit_move_id = move.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
        }

    def action_cancel(self):
        for rec in self:
            if rec.state in ("restocked", "repaired", "scrapped"):
                raise UserError(_(
                    "A closed return cannot be cancelled."))
            rec.state = "cancelled"


class ReturnFlowLine(models.Model):
    _name = "return.flow.line"
    _description = "Return Line"
    _order = "request_id, id"

    request_id = fields.Many2one(
        "return.flow.request", required=True, ondelete="cascade", index=True)
    move_id = fields.Many2one("stock.move", string="Delivery Move")
    product_id = fields.Many2one(
        "product.product", string="Product", required=True)
    uom_id = fields.Many2one("uom.uom", string="Unit")
    qty_delivered = fields.Float(string="Delivered Quantity", default=0.0)
    qty = fields.Float(string="Returned Quantity", default=0.0)
    company_id = fields.Many2one(
        related="request_id.company_id", store=True, readonly=True)

    _request_product_uniq = models.Constraint(
        "UNIQUE(request_id, product_id, move_id)",
        "This delivery line is already part of the return.")

    @api.constrains("qty", "qty_delivered")
    def _check_qty(self):
        for line in self:
            if line.qty < -EPS:
                raise ValidationError(_(
                    "The returned quantity of %s cannot be negative.",
                    line.product_id.display_name))
            if line.qty - line.qty_delivered > EPS:
                raise ValidationError(_(
                    "You cannot return more than delivered for %s "
                    "(delivered %s, returned %s).",
                    line.product_id.display_name,
                    line.qty_delivered, line.qty))

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.product_id and not self.uom_id:
            self.uom_id = self.product_id.uom_id
