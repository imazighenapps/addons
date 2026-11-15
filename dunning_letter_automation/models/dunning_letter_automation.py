# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DunningLevel(models.Model):
    _name = "dunning.letter.level"
    _description = "Dunning Level"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    days_after_due = fields.Integer(
        string="Days After Due", default=7, required=True,
        help="Number of days past the due date before this level applies.")
    subject = fields.Char(translate=True)
    body = fields.Text(translate=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.constrains("days_after_due")
    def _check_days(self):
        for level in self:
            if level.days_after_due < 0:
                raise ValidationError(
                    _("Days after due date cannot be negative."))


class DunningLetter(models.Model):
    _name = "dunning.letter"
    _description = "Dunning Letter"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True,
        tracking=True)
    move_id = fields.Many2one(
        "account.move", string="Invoice", ondelete="set null", index=True,
        tracking=True)
    level_id = fields.Many2one(
        "dunning.letter.level", string="Level", required=True, index=True,
        tracking=True)
    due_date = fields.Date(index=True)
    amount_residual = fields.Monetary(
        string="Residual Amount", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    sent_date = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"), ("paid", "Paid"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("dunning.letter")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Dunning Letter",
                        "code": "dunning.letter",
                        "prefix": "DUN/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_send(self):
        for letter in self:
            if letter.state != "draft":
                raise UserError(
                    _("Only a draft letter can be sent."))
            letter.write({
                "state": "sent",
                "sent_date": fields.Date.context_today(letter),
            })
            letter.message_post(body=_(
                "Dunning letter %(name)s sent to %(partner)s.",
                name=letter.name,
                partner=letter.partner_id.display_name))
            if letter.move_id:
                letter.move_id.message_post(body=_(
                    "Dunning level %(level)s: letter %(name)s sent.",
                    level=letter.level_id.name, name=letter.name))
        return True

    def action_mark_paid(self):
        for letter in self:
            if letter.state not in ("draft", "sent"):
                raise UserError(
                    _("Only a draft or sent letter can be marked paid."))
            letter.state = "paid"
        return True

    def action_cancel(self):
        for letter in self:
            if letter.state in ("paid", "cancelled"):
                raise UserError(
                    _("A paid or cancelled letter cannot be cancelled."))
            letter.state = "cancelled"
        return True

    def action_reset_draft(self):
        for letter in self:
            if letter.state != "cancelled":
                raise UserError(
                    _("Only a cancelled letter can be reset to draft."))
            letter.write({"state": "draft", "sent_date": False})
        return True


class DunningGenerate(models.TransientModel):
    _name = "dunning.generate"
    _description = "Generate Dunning Letters"

    as_of_date = fields.Date(
        string="As Of", required=True, default=fields.Date.context_today)
    level_ids = fields.Many2many(
        "dunning.letter.level", string="Levels",
        help="Leave empty to use every active level of the company.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)

    def action_generate(self):
        self.ensure_one()
        levels = self.level_ids or self.env["dunning.letter.level"].search([
            ("company_id", "=", self.company_id.id),
            ("active", "=", True),
        ])
        if not levels:
            raise UserError(_("Create at least one active dunning level."))
        Move = self.env["account.move"]
        Letter = self.env["dunning.letter"]
        created = Letter
        for level in levels.sorted(lambda item: (item.sequence, item.id)):
            cutoff = self.as_of_date - timedelta(days=level.days_after_due)
            domain = [
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("company_id", "=", self.company_id.id),
                ("payment_state", "in", ("not_paid", "partial")),
                ("invoice_date_due", "<=", cutoff),
            ]
            already = Letter.search([
                ("level_id", "=", level.id),
                ("state", "in", ("draft", "sent")),
            ]).mapped("move_id")
            moves = Move.search(domain) - already
            for move in moves:
                created |= Letter.create({
                    "partner_id": move.partner_id.id,
                    "move_id": move.id,
                    "level_id": level.id,
                    "due_date": move.invoice_date_due,
                    "amount_residual": move.amount_residual,
                    "currency_id": move.currency_id.id
                    or self.company_id.currency_id.id,
                    "company_id": self.company_id.id,
                    "note": level.body,
                })
        action = self.env["ir.actions.actions"]._for_xml_id(
            "dunning_letter_automation.action_dunning_letter")
        if created:
            action["domain"] = [("id", "in", created.ids)]
        return action
