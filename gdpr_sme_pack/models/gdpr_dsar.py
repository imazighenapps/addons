# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class GdprDsar(models.Model):
    _name = "gdpr.dsar"
    _description = "GDPR Data Subject Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "deadline asc"

    name = fields.Char(default="/", copy=False, readonly=True)
    partner_id = fields.Many2one("res.partner", string="Data Subject")
    requester_name = fields.Char(string="Requester Name")
    requester_email = fields.Char(string="Requester Email")
    channel = fields.Selection(
        [("portal", "Portal"), ("email", "Email"), ("manual", "Manual")],
        default="manual",
    )
    right = fields.Selection(
        [("access", "Access (Art.15)"), ("rectification", "Rectification (Art.16)"),
         ("erasure", "Erasure (Art.17)"), ("restriction", "Restriction (Art.18)"),
         ("portability", "Portability (Art.20)"), ("objection", "Objection (Art.21)"),
         ("auto", "Automated Decision (Art.22)"), ("withdraw", "Withdraw Consent")],
        required=True,
    )
    receipt_date = fields.Date(string="Received On (T0)", default=fields.Date.today,
                               required=True)
    deadline = fields.Date(compute="_compute_deadline", store=True)
    extension = fields.Boolean(string="Extended +2 Months")
    extension_reason = fields.Text()
    identity_state = fields.Selection(
        [("pending", "Pending"), ("verified", "Verified"), ("doubtful", "Doubtful")],
        default="pending",
        tracking=True,
    )
    state = fields.Selection(
        [("new", "New"), ("identity", "Identity Check"), ("search", "Search"),
         ("processing", "Processing"), ("answered", "Answered"),
         ("refused", "Refused"), ("overdue", "Overdue")],
        default="new",
        tracking=True,
    )
    assignee_id = fields.Many2one("res.users", string="Assignee")
    processing_ids = fields.Many2many("gdpr.activity", string="Related Processing")
    response_doc = fields.Text(string="Response")
    refusal_reason = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("gdpr.dsar") or "/"
        res = super().create(vals_list)
        for rec in res:
            rec.message_post(body=_("DSAR received; 1-month clock started."))
        return res

    @api.depends("receipt_date", "extension")
    def _compute_deadline(self):
        for rec in self:
            base = rec.receipt_date or fields.Date.today()
            months = 3 if rec.extension else 1
            rec.deadline = base + relativedelta(months=months)

    def action_answer(self):
        self.write({"state": "answered"})

    def action_refuse(self):
        for rec in self:
            if not rec.refusal_reason:
                from odoo.exceptions import UserError
                raise UserError(_("A refusal reason with legal remedies is required."))
            rec.state = "refused"

    def action_extend(self):
        for rec in self:
            if not rec.extension_reason:
                from odoo.exceptions import UserError
                raise UserError(_("An extension reason is required."))
            rec.write({"state": "processing", "extension": True})

    @api.model
    def _cron_check_sla(self):
        today = fields.Date.today()
        soon = self.search([("state", "not in", ("answered", "refused", "overdue")),
                            ("deadline", "=", today + relativedelta(days=7))])
        for rec in soon:
            rec.activity_schedule(
                "mail.mail_activity_data_todo", user_id=rec.assignee_id.id or rec.env.uid,
                summary=_("DSAR deadline in 7 days: %s") % rec.name)
        late = self.search([("state", "not in", ("answered", "refused", "overdue")),
                            ("deadline", "<", today)])
        late.write({"state": "overdue"})
        return True
