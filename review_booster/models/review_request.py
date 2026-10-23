# -*- coding: utf-8 -*-
import secrets
from odoo import api, fields, models, _


class ReviewRequest(models.Model):
    _name = "review.request"
    _description = "Google Review Request"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    name = fields.Char(default="/", copy=False, readonly=True)
    campaign_id = fields.Many2one("review.campaign", required=True,
                                  ondelete="restrict")
    partner_id = fields.Many2one("res.partner", required=True)
    move_id = fields.Many2one("account.move", string="Invoice")
    picking_id = fields.Many2one("stock.picking", string="Delivery")
    token = fields.Char(default=lambda self: secrets.token_hex(12), copy=False,
                        required=True)
    state = fields.Selection(
        [("pending", "Pending"), ("sent", "Sent"), ("clicked", "Clicked"),
         ("reviewed", "Reviewed"), ("optout", "Opted Out")],
        default="pending",
        tracking=True,
    )
    send_on = fields.Date()
    sent_on = fields.Datetime(readonly=True)
    clicked_on = fields.Datetime(readonly=True)

    _token_unique = models.Constraint("UNIQUE(token)", "Token must be unique.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("review.request") or "/"
        return super().create(vals_list)

    def review_link(self):
        self.ensure_one()
        base = self.env["ir.config_parameter"].sudo().get_str("web.base.url", "")
        return "%s/r/%s" % (base.rstrip("/"), self.token)

    def action_send(self):
        for rec in self:
            if not rec.partner_id.review_optin:
                rec.state = "optout"
                continue
            template = self.env.ref("review_booster.mail_review_request",
                                    raise_if_not_found=False)
            if template:
                template.send_mail(rec.id, force_send=False)
            rec.write({"state": "sent", "sent_on": fields.Datetime.now()})

    def action_mark_reviewed(self):
        self.write({"state": "reviewed"})

    def action_optout(self):
        for rec in self:
            rec.partner_id.write({"review_optin": False})
            rec.state = "optout"

    @api.model
    def _cron_send_due(self):
        from datetime import date, timedelta
        due = self.search([("state", "=", "pending"),
                           ("send_on", "<=", date.today())])
        due.action_send()
        return True


class ReviewPartner(models.Model):
    _inherit = "res.partner"

    review_optin = fields.Boolean(string="Agrees to Review Requests")
    review_optin_date = fields.Date()
    review_optin_proof = fields.Char(string="Opt-in Proof")
