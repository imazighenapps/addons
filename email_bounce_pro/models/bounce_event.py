# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class BounceEvent(models.Model):
    _name = "bounce.event"
    _description = "Email Bounce"
    _order = "bounce_date desc, id desc"

    partner_id = fields.Many2one("res.partner", string="Contact")
    email = fields.Char()
    message_id = fields.Many2one(
        "mail.message", string="Message", readonly=True,
        ondelete="set null")
    notification_id = fields.Many2one(
        "mail.notification", string="Notification", readonly=True,
        ondelete="set null")
    bounce_date = fields.Datetime(default=fields.Datetime.now)
    reason = fields.Char()
    state = fields.Selection(
        [("new", "New"), ("handled", "Handled"), ("ignored", "Ignored")],
        default="new", required=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    def action_handle(self):
        for event in self:
            event.write({"state": "handled"})
        return True

    def action_ignore(self):
        for event in self:
            event.write({"state": "ignored"})
        return True

    def action_reopen(self):
        for event in self:
            event.write({"state": "new"})
        return True


class BounceScanWizard(models.TransientModel):
    _name = "bounce.scan.wizard"
    _description = "Bounce Scan"

    name = fields.Char(default="Bounce scan")
    date_from = fields.Datetime()
    date_to = fields.Datetime()
    rule_ids = fields.Many2many("bounce.guard.rule", string="Rules")

    def action_scan(self):
        """File every bounced notification not already registered."""
        # mail.notification carries no date on the series we support: the
        # window is read through the message it belongs to.
        domain = [("notification_type", "=", "email"),
                  ("notification_status", "=", "bounce")]
        if self.date_from:
            domain.append(("mail_message_id.date", ">=", self.date_from))
        if self.date_to:
            domain.append(("mail_message_id.date", "<=", self.date_to))
        rules = self.rule_ids
        if not rules:
            rules = self.env["bounce.guard.rule"].search([
                ("company_id", "=", self.env.company.id)])
        threshold = rules[:1].threshold or 2
        seen = self.env["bounce.event"].search([]).mapped("notification_id")
        notifications = self.env["mail.notification"].search(domain) - seen
        for notification in notifications:
            partner = notification.res_partner_id
            values = {
                "partner_id": partner.id,
                "email": partner.email or "",
                "reason": notification.failure_reason or "",
                "notification_id": notification.id,
                "message_id": notification.mail_message_id.id,
                "bounce_date": notification.mail_message_id.date
                or fields.Datetime.now(),
                "company_id": self.env.company.id,
            }
            self.env["bounce.event"].create(values)
        for partner in notifications.mapped("res_partner_id"):
            count = self.env["bounce.event"].search_count([
                ("partner_id", "=", partner.id),
                ("state", "=", "new"),
            ])
            if count >= threshold:
                partner.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary=_("Bounced address"),
                    note=_("This address bounced %s times.")
                    % count,
                    user_id=(rules.notify_user_id or self.env.user).id,
                )
        return True
