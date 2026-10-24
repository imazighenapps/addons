# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


class StockAlertRequest(models.Model):
    _name = "stock.alert.request"
    _description = "Back in Stock Request"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, tracking=True,
        ondelete="cascade")
    product_tmpl_id = fields.Many2one(
        "product.template", related="product_id.product_tmpl_id",
        store=True, index=True)
    partner_id = fields.Many2one("res.partner", string="Contact")
    email = fields.Char(required=True, tracking=True)
    state = fields.Selection(
        [("pending", "Waiting"), ("notified", "Notified"),
         ("cancelled", "Cancelled")],
        default="pending", required=True, tracking=True, index=True)
    source = fields.Selection(
        [("manual", "Back Office"), ("api", "Website")],
        default="manual", required=True)
    consent_date = fields.Datetime(default=fields.Datetime.now, readonly=True)
    notified_date = fields.Datetime(readonly=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    note = fields.Text()
    active = fields.Boolean(default=True)

    @api.depends("product_id", "email")
    def _compute_name(self):
        for request in self:
            request.name = "%s - %s" % (
                request.product_id.display_name or _("Product"),
                request.email or "")

    @api.constrains("email")
    def _check_email(self):
        for request in self:
            if request.email and not EMAIL_RE.match(request.email):
                raise UserError(_("Invalid email address: %s") % request.email)

    def action_notify(self):
        template = self.env.ref(
            "back_in_stock_pro.mail_template_stock_alert",
            raise_if_not_found=False)
        for request in self:
            if request.state != "pending":
                continue
            if template:
                template.send_mail(request.id, force_send=False)
            request.write({
                "state": "notified",
                "notified_date": fields.Datetime.now(),
            })
            request.message_post(body=_(
                "Back-in-stock email sent to %s.", request.email))
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset(self):
        self.write({"state": "pending", "notified_date": False})

    @api.model
    def _cron_notify(self):
        pending = self.search([("state", "=", "pending")])
        for request in pending:
            product = request.product_id
            if product and product.qty_available > 0:
                request.action_notify()
        return True

    @api.model
    def subscribe(self, product_id, email, partner_id=None):
        email = (email or "").strip().lower()
        if not email or not EMAIL_RE.match(email):
            raise UserError(_("Please enter a valid email address."))
        product = self.env["product.product"].browse(int(product_id))
        if not product.exists():
            raise UserError(_("Unknown product."))
        existing = self.search([
            ("product_id", "=", product.id),
            ("email", "=", email),
            ("state", "=", "pending"),
        ], limit=1)
        if existing:
            return existing
        return self.create({
            "product_id": product.id,
            "email": email,
            "partner_id": partner_id or False,
            "source": "api",
        })


class ProductTemplate(models.Model):
    _inherit = "product.template"

    alert_request_count = fields.Integer(
        string="Stock Alerts", compute="_compute_alert_request_count")

    def _compute_alert_request_count(self):
        Request = self.env["stock.alert.request"]
        for template in self:
            template.alert_request_count = Request.search_count([
                ("product_tmpl_id", "=", template.id),
                ("state", "=", "pending"),
            ])

    def action_view_alerts(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Stock Alerts"),
            "res_model": "stock.alert.request",
            "view_mode": "list,form",
            "domain": [("product_tmpl_id", "=", self.id)],
            "context": {"default_product_id": self.product_variant_id.id},
        }
