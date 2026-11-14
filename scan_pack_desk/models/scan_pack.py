# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class ScanPackSession(models.Model):
    _name = "scan_pack.session"
    _description = "Scan Pack Session"
    _order = "create_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    picking_id = fields.Many2one(
        "stock.picking", string="Pick Order", required=True, index=True,
        ondelete="cascade",
        help="The picking this scan session prepares.")
    state = fields.Selection(
        [("open", "Open"), ("validated", "Validated")],
        default="open", required=True, copy=False, index=True)
    scan_code = fields.Char(
        string="Scan Input",
        help="Scan or type a product barcode, then confirm. The prepared "
             "quantity of the matching pick line grows accordingly.")
    scan_qty = fields.Float(
        string="Quantity per Scan", default=1.0,
        help="Quantity added by one scan. Keep it at 1 for unit picking, "
             "or scan a whole pack at once.")
    move_ids = fields.One2many(
        "scan_pack.move", "session_id", string="Pick Lines", copy=False)
    log_ids = fields.One2many(
        "scan_pack.log", "session_id", string="Scan Journal", copy=False)
    scanned_qty = fields.Float(
        compute="_compute_totals", string="Prepared Quantity")
    demand_qty = fields.Float(
        compute="_compute_totals", string="Requested Quantity")
    difference_qty = fields.Float(
        compute="_compute_totals", string="Difference",
        help="Requested quantity minus prepared quantity. Zero means the "
             "preparation matches the pick order.")
    is_balanced = fields.Boolean(
        compute="_compute_totals", string="Balanced",
        help="True when the prepared quantity matches the requested "
             "quantity on every pick line.")
    last_result = fields.Selection(
        [("accepted", "Accepted"), ("unknown", "Unknown"),
         ("excess", "Excess"), ("exception", "Exception"),
         ("validated", "Validated"), ("reopened", "Reopened")],
        compute="_compute_last", string="Last Scan")
    last_message = fields.Text(compute="_compute_last", string="Last Message")
    has_exception = fields.Boolean(
        string="Manager Exception", copy=False,
        help="True when a manager authorized the validation of this "
             "session despite a preparation gap.")
    exception_reason = fields.Text(
        string="Exception Reason", copy=False,
        help="Mandatory reason given by the manager; it is also written "
             "to the scan journal.")
    exception_by_id = fields.Many2one(
        "res.users", string="Exception By", readonly=True, copy=False)
    exception_date = fields.Datetime(
        string="Exception Date", readonly=True, copy=False)
    validated_by_id = fields.Many2one(
        "res.users", string="Validated By", readonly=True, copy=False)
    validated_at = fields.Datetime(
        string="Validated At", readonly=True, copy=False)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('picking_uniq', "UNIQUE(picking_id)", "One scan session per picking. Reopen the existing session instead "
        "of creating a new one."),
    ]

    @api.depends("picking_id", "picking_id.name", "state")
    def _compute_name(self):
        for session in self:
            session.name = "%s (%s)" % (
                session.picking_id.name or _("Pick Order"), session.state)

    @api.depends("move_ids.scanned_qty", "move_ids.demand_qty")
    def _compute_totals(self):
        for session in self:
            scanned = sum(session.move_ids.mapped("scanned_qty"))
            demand = sum(session.move_ids.mapped("demand_qty"))
            session.scanned_qty = scanned
            session.demand_qty = demand
            session.difference_qty = demand - scanned
            session.is_balanced = bool(session.move_ids) and all(
                session.move_ids.mapped("is_complete"))

    @api.depends("log_ids")
    def _compute_last(self):
        for session in self:
            last = session.log_ids[:1]
            session.last_result = last.result
            session.last_message = last.message

    @api.constrains("scan_qty")
    def _check_scan_qty(self):
        for session in self:
            if session.scan_qty <= 0:
                raise ValidationError(_(
                    "The quantity per scan must be strictly positive."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            picking_id = vals.get("picking_id")
            if picking_id and self.search_count(
                    [("picking_id", "=", picking_id)]):
                raise ValidationError(_(
                    "This picking already has a scan session: reopen it "
                    "instead of creating a new one."))
        sessions = super().create(vals_list)
        for session in sessions:
            session._refresh_lines()
        return sessions

    def write(self, vals):
        locked = set(vals) - {"note", "state"}
        for session in self:
            if session.state == "validated" and locked:
                raise UserError(_(
                    "The scan session of the picking \"%s\" is validated: "
                    "reopen it before changing anything.",
                    session.picking_id.name))
        return super().write(vals)

    def _refresh_lines(self):
        """One pick line per active move of the picking."""
        self.ensure_one()
        existing_ids = set(self.move_ids.mapped("move_id").ids)
        moves = self.picking_id.move_ids.filtered(
            lambda move: move.state != "cancel" and move.product_uom_qty)
        for move in moves:
            if move.id not in existing_ids:
                self.env["scan_pack.move"].create({
                    "session_id": self.id, "move_id": move.id})

    def _log(self, product, barcode, qty, result, message):
        """Write one immutable journal entry for this session."""
        self.ensure_one()
        return self.env["scan_pack.log"].create({
            "session_id": self.id,
            "product_id": product.id if product else False,
            "barcode": barcode or "", "qty": qty, "result": result,
            "message": message, "company_id": self.company_id.id,
        })

    def _find_product(self, barcode):
        product = self.env["product.product"].with_context(
            active_test=False).search([("barcode", "=", barcode)], limit=1)
        if not product:
            product = self.env["product.product"].with_context(
                active_test=False).search(
                    [("default_code", "=", barcode)], limit=1)
        return product

    def _apply_scan(self, barcode):
        """Apply one scan: grow the right line or refuse and journal it.

        Refusals are journal entries, not exceptions: an exception would
        roll back the journal entry that proves the refusal.
        """
        self.ensure_one()
        product = self._find_product(barcode)
        if not product:
            self._log(product, barcode, 0.0, "unknown",
                      _("Barcode not found in the product catalog: %s",
                        barcode))
            return
        lines = self.move_ids.filtered(
            lambda line: line.product_id == product)
        if not lines:
            self._log(product, barcode, 0.0, "unknown",
                      _("Product %s is not part of this pick order.",
                        product.display_name))
            return
        line = lines.filtered(
            lambda entry: not entry.is_complete)[:1] or lines[:1]
        if line.is_complete:
            self._log(product, barcode, 0.0, "excess",
                      _("%s is already fully prepared (%s of %s).",
                        product.display_name, line.scanned_qty,
                        line.demand_qty))
            return
        if line.scanned_qty + self.scan_qty > line.demand_qty + EPS:
            self._log(product, barcode, 0.0, "excess",
                      _("Scanning %s would exceed the requested quantity "
                        "of %s.", self.scan_qty, product.display_name))
            return
        line.scanned_qty += self.scan_qty
        self._log(product, barcode, self.scan_qty, "accepted",
                  _("Accepted: %s now prepared %s of %s.",
                    product.display_name, line.scanned_qty,
                    line.demand_qty))

    def action_scan(self):
        for session in self:
            if session.state == "validated":
                raise UserError(_("This scan session is closed."))
            barcode = (session.scan_code or "").strip()
            if not barcode:
                raise UserError(_("Scan a barcode first."))
            session._apply_scan(barcode)
            session.scan_code = False
        return True

    def action_refresh_lines(self):
        for session in self:
            if session.state == "validated":
                raise UserError(_("This scan session is closed."))
            session._refresh_lines()
        return True

    def action_grant_exception(self):
        for session in self:
            if session.state == "validated":
                raise UserError(_("This scan session is closed."))
            if not self.env.user.has_group("stock.group_stock_manager"):
                raise UserError(_(
                    "Only a warehouse manager can grant an exception."))
            reason = (session.exception_reason or "").strip()
            if len(reason) < 10:
                raise UserError(_(
                    "A manager exception needs a reason of at least 10 "
                    "characters: it stays in the scan journal next to the "
                    "validated gap."))
            session.has_exception = True
            session.exception_by_id = self.env.user
            session.exception_date = fields.Datetime.now()
            session._log(False, "", 0.0, "exception",
                         _("Manager exception granted: %s", reason))
        return True

    def _guard_validation(self):
        """Block validation while prepared differs from requested.

        Called with sudo from the picking validation: the guard is a
        process rule, not a permission.
        """
        self.ensure_one()
        self._refresh_lines()
        if self.is_balanced:
            return
        if self.has_exception:
            return
        details = "\n".join(
            _("%(product)s: %(scanned)s prepared / %(demand)s requested",
              product=line.product_id.display_name,
              scanned=line.scanned_qty, demand=line.demand_qty)
            for line in self.move_ids.filtered(
                lambda entry: not entry.is_complete))
        raise UserError(_(
            "Scan Pack: the prepared quantity does not match the pick "
            "order.\n\n%(details)s\n\nFinish the preparation, or have a "
            "warehouse manager grant an exception with a reason.",
            details=details))

    def _close_after_validation(self):
        self.ensure_one()
        # One single write: the next field assignment would hit the
        # validated-session lock (the guard reads the current state).
        self.write({
            "state": "validated",
            "validated_by_id": self.env.user.id,
            "validated_at": fields.Datetime.now(),
        })
        short = self.move_ids.filtered(lambda line: not line.is_complete)
        if short:
            self._log(short[:1].product_id, "", 0.0, "exception",
                      _("Validated with a manager exception: %s",
                        self.exception_reason))
        self._log(False, "", 0.0, "validated",
                  _("Picking validated with %s prepared of %s requested.",
                    self.scanned_qty, self.demand_qty))

    def action_reopen(self):
        for session in self:
            if session.state != "validated":
                raise UserError(_("Only a validated session can reopen."))
            if session.picking_id.state == "done":
                raise UserError(_(
                    "The picking \"%s\" is done: unlock it before "
                    "re-preparing.", session.picking_id.name))
            session.state = "open"
            session._log(False, "", 0.0, "reopened",
                         _("Scan session reopened."))
        return True


class ScanPackMove(models.Model):
    _name = "scan_pack.move"
    _description = "Scan Pack Pick Line"
    _order = "session_id, move_id, id"

    session_id = fields.Many2one(
        "scan_pack.session", string="Scan Session", required=True,
        ondelete="cascade", index=True)
    move_id = fields.Many2one(
        "stock.move", string="Pick Order Line", required=True,
        ondelete="cascade", index=True)
    product_id = fields.Many2one(
        "product.product", related="move_id.product_id", store=True,
        readonly=True)
    demand_qty = fields.Float(
        related="move_id.product_uom_qty", store=True, readonly=True,
        string="Requested Quantity")
    scanned_qty = fields.Float(
        string="Prepared Quantity", default=0.0, copy=False,
        help="Grows by one scan (or the session quantity per scan).")
    difference_qty = fields.Float(
        compute="_compute_state", string="Difference", store=True)
    is_complete = fields.Boolean(compute="_compute_state",
                                 string="Complete", store=True)
    company_id = fields.Many2one(
        related="session_id.company_id", store=True, readonly=True)

    _sql_constraints = [
        ('session_move_uniq', "UNIQUE(session_id, move_id)", "One pick line per move in a scan session."),
    ]

    @api.depends("demand_qty", "scanned_qty")
    def _compute_state(self):
        for line in self:
            line.difference_qty = line.demand_qty - line.scanned_qty
            line.is_complete = line.scanned_qty >= line.demand_qty - EPS

    @api.constrains("scanned_qty")
    def _check_scanned(self):
        for line in self:
            if line.scanned_qty < -EPS:
                raise ValidationError(_(
                    "The prepared quantity of %s cannot be negative.",
                    line.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("session_id") and vals.get("move_id") \
                    and self.search_count(
                        [("session_id", "=", vals["session_id"]),
                         ("move_id", "=", vals["move_id"])]):
                raise ValidationError(_(
                    "This pick order line already has a pick line in this "
                    "scan session."))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.session_id.state == "validated":
                raise UserError(_(
                    "The scan session of the picking \"%s\" is validated: "
                    "reopen it before scanning again.",
                    line.session_id.picking_id.name))
        return super().write(vals)


class ScanPackLog(models.Model):
    _name = "scan_pack.log"
    _description = "Scan Pack Journal"
    _order = "create_date desc, id desc"

    session_id = fields.Many2one(
        "scan_pack.session", string="Scan Session", required=True,
        ondelete="cascade", index=True)
    user_id = fields.Many2one(
        "res.users", string="Scanned By", default=lambda self: self.env.user,
        required=True, readonly=True)
    product_id = fields.Many2one(
        "product.product", string="Product", readonly=True)
    barcode = fields.Char(readonly=True,
                          help="The scanned barcode or internal reference.")
    qty = fields.Float(string="Quantity", readonly=True)
    result = fields.Selection(
        [("accepted", "Accepted"), ("unknown", "Unknown"),
         ("excess", "Excess"), ("exception", "Exception"),
         ("validated", "Validated"), ("reopened", "Reopened")],
        readonly=True, required=True)
    message = fields.Text(readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, readonly=True)

    def write(self, vals):
        if vals:
            raise UserError(_(
                "The scan journal is immutable: it is the proof of who "
                "scanned what, when and why."))
        return super().write(vals)

    def unlink(self):
        raise UserError(_(
            "The scan journal is immutable: entries can never be deleted."))
        return super().unlink()


class ScanPackPicking(models.Model):
    _inherit = "stock.picking"

    scan_session_ids = fields.One2many(
        "scan_pack.session", "picking_id", string="Scan Sessions")

    def action_open_scan_session(self):
        """Open the scan screen of this picking, creating it if needed."""
        self.ensure_one()
        session = self.env["scan_pack.session"].sudo().search(
            [("picking_id", "=", self.id)], limit=1)
        if not session:
            session = self.env["scan_pack.session"].sudo().create({
                "picking_id": self.id})
        elif session.state == "validated":
            raise UserError(_(
                "The scan session of the picking \"%s\" is validated: "
                "reopen it before scanning again.", session.name))
        return {
            "type": "ir.actions.act_window",
            "name": _("Scan Screen"),
            "res_model": "scan_pack.session",
            "res_id": session.id,
            "view_mode": "form",
            "target": "current",
        }

    def button_validate(self):
        for picking in self:
            session = self.env["scan_pack.session"].sudo().search(
                [("picking_id", "=", picking.id), ("state", "=", "open")],
                limit=1)
            if session:
                session._guard_validation()
        res = super().button_validate()
        for picking in self:
            if picking.state == "done":
                session = self.env["scan_pack.session"].sudo().search(
                    [("picking_id", "=", picking.id), ("state", "=", "open")],
                    limit=1)
                if session:
                    session._close_after_validation()
        return res
