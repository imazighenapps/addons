# -*- coding: utf-8 -*-
import re
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


def _clean_iban(iban):
    return (iban or "").replace(" ", "").upper()


def _is_valid_iban(iban):
    iban = _clean_iban(iban)
    if not re.match(r"^[A-Z]{2}[0-9A-Z]{13,32}$", iban):
        return False
    rearranged = iban[4:] + iban[:4]
    digits = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    try:
        return int(digits) % 97 == 1
    except Exception:
        return False


class SddMandate(models.Model):
    _name = "sdd.mandate"
    _description = "SEPA Direct Debit Mandate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _rec_name = "name"

    name = fields.Char(
        string="Mandate Reference", required=True, copy=False, index=True,
        default="New", tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True,
        default=lambda self: self.env.company, index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Debtor", required=True, tracking=True, index=True)
    partner_bank_id = fields.Many2one(
        "res.partner.bank", string="Debtor Bank Account", required=True, tracking=True,
        domain="[('partner_id', '=', partner_id)]")
    debtor_iban = fields.Char(
        string="IBAN", compute="_compute_debtor_iban", store=True, readonly=True)
    debtor_bic = fields.Char(
        string="BIC", compute="_compute_debtor_bic", store=True, readonly=True)
    scheme = fields.Selection([
        ("CORE", "CORE"),
        ("B2B", "B2B"),
    ], string="Scheme", default="CORE", required=True, tracking=True)
    sequence_type = fields.Selection([
        ("FRST", "First (FRST)"),
        ("RCUR", "Recurrent (RCUR)"),
        ("FNAL", "Final (FNAL)"),
        ("OOFF", "One-Off (OOFF)"),
    ], string="Next Sequence Type", default="FRST", required=True, tracking=True)
    signature_date = fields.Date(string="Signature Date", required=True, tracking=True)
    activation_date = fields.Date(string="Activation Date", tracking=True, readonly=True)
    revocation_date = fields.Date(string="Revocation Date", tracking=True, readonly=True)
    expiry_date = fields.Date(string="Expiry Date", tracking=True)
    last_debit_date = fields.Date(string="Last Collection Date", readonly=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("revoked", "Revoked"),
        ("expired", "Expired"),
        ("closed", "Closed"),
    ], string="Status", default="draft", required=True, tracking=True, index=True)
    signed_document_ids = fields.Many2many(
        "ir.attachment", "sdd_mandate_attachment_rel", "mandate_id", "attachment_id",
        string="Signed Documents")
    rib_history_ids = fields.One2many(
        "sdd.mandate.rib.history", "mandate_id", string="Bank Account History")
    batch_line_ids = fields.One2many("sdd.batch.line", "mandate_id", string="Collection Lines")
    batch_count = fields.Integer(compute="_compute_batch_count")
    note = fields.Text(string="Internal Notes")
    alert_expiring = fields.Boolean(string="Expiring Soon", compute="_compute_alerts", store=True)
    active_flag = fields.Boolean(string="Active Record", default=True)

    _sql_constraints = [
        ("name_company_uniq", "unique(name, company_id)", "The mandate reference must be unique per company."),
    ]

    @api.depends("partner_bank_id")
    def _compute_debtor_iban(self):
        for mandate in self:
            bank = mandate.partner_bank_id
            acc = (bank.acc_number if "acc_number" in bank._fields else bank.account_number) if bank else False
            mandate.debtor_iban = _clean_iban(acc)

    @api.depends("partner_bank_id", "partner_bank_id.bank_bic")
    def _compute_debtor_bic(self):
        for mandate in self:
            mandate.debtor_bic = (mandate.partner_bank_id.bank_bic or "").upper() if mandate.partner_bank_id else False

    @api.depends("batch_line_ids.batch_id")
    def _compute_batch_count(self):
        for mandate in self:
            mandate.batch_count = len(mandate.batch_line_ids.mapped("batch_id"))

    @api.depends("state", "expiry_date")
    def _compute_alerts(self):
        today = fields.Date.context_today(self)
        soon = today + timedelta(days=30)
        for mandate in self:
            mandate.alert_expiring = bool(
                mandate.state == "active"
                and mandate.expiry_date
                and today <= mandate.expiry_date <= soon
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("sdd.mandate") or _("New")
        return super().create(vals_list)

    @api.constrains("partner_bank_id", "partner_id")
    def _check_iban(self):
        for mandate in self:
            if mandate.partner_bank_id and mandate.partner_bank_id.partner_id != mandate.partner_id:
                raise ValidationError(_("The selected bank account does not belong to the debtor."))
            iban = mandate.debtor_iban
            if not _is_valid_iban(iban):
                raise ValidationError(_("Invalid IBAN for mandate %s.") % mandate.name)

    @api.constrains("expiry_date", "signature_date")
    def _check_dates(self):
        for mandate in self:
            if mandate.expiry_date and mandate.signature_date and mandate.expiry_date < mandate.signature_date:
                raise ValidationError(_("The expiry date cannot be earlier than the signature date."))

    def action_activate(self):
        today = fields.Date.context_today(self)
        for mandate in self.filtered(lambda m: m.state in ("draft", "suspended")):
            mandate.write({"state": "active", "activation_date": mandate.activation_date or today})

    def action_suspend(self):
        self.filtered(lambda m: m.state == "active").write({"state": "suspended"})

    def action_revoke(self):
        today = fields.Date.context_today(self)
        self.filtered(lambda m: m.state in ("draft", "active", "suspended")).write({
            "state": "revoked",
            "revocation_date": today,
        })

    def action_close(self):
        self.filtered(lambda m: m.state in ("active", "suspended", "expired")).write({
            "state": "closed",
            "sequence_type": "FNAL",
        })

    def action_reset_to_draft(self):
        self.filtered(lambda m: m.state in ("suspended", "revoked", "expired", "closed")).write({
            "state": "draft",
            "revocation_date": False,
        })

    def consume_sequence(self):
        """Update mandate sequence after it has been used in a generated batch."""
        today = fields.Date.context_today(self)
        for mandate in self:
            seq = mandate.sequence_type
            if seq == "FRST":
                mandate.sequence_type = "RCUR"
            elif seq == "OOFF":
                mandate.state = "closed"
            mandate.last_debit_date = today

    def action_view_batches(self):
        self.ensure_one()
        batches = self.batch_line_ids.mapped("batch_id")
        action = self.env["ir.actions.actions"]._for_xml_id("sepa_direct_debit.action_sdd_batch")
        if len(batches) == 1:
            action.update({"view_mode": "form", "res_id": batches.id, "views": []})
        else:
            action["domain"] = [("id", "in", batches.ids)]
        return action

    @api.model
    def _cron_check_expiry(self):
        today = fields.Date.context_today(self)
        expired = self.search([
            ("state", "=", "active"),
            ("expiry_date", "!=", False),
            ("expiry_date", "<", today),
        ])
        expired.write({"state": "expired"})
        expiring = self.search([
            ("state", "=", "active"),
            ("expiry_date", "!=", False),
            ("expiry_date", ">=", today),
            ("expiry_date", "<=", today + timedelta(days=30)),
        ])
        for mandate in expiring:
            mandate.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=_("SEPA mandate expiring soon"),
                note=_("Mandate %s expires on %s.") % (mandate.name, mandate.expiry_date),
                user_id=mandate.create_uid.id or self.env.user.id,
            )
        return True


class SddMandateRibHistory(models.Model):
    _name = "sdd.mandate.rib.history"
    _description = "SEPA Mandate Bank Account History"
    _order = "change_date desc, id desc"

    mandate_id = fields.Many2one("sdd.mandate", required=True, ondelete="cascade", index=True)
    change_date = fields.Date(string="Change Date", required=True, default=fields.Date.context_today)
    old_iban = fields.Char(string="Previous IBAN")
    old_bic = fields.Char(string="Previous BIC")
    new_iban = fields.Char(string="New IBAN", required=True)
    new_bic = fields.Char(string="New BIC")
    reason = fields.Char(string="Reason")

    @api.constrains("new_iban")
    def _check_new_iban(self):
        for history in self:
            if not _is_valid_iban(history.new_iban):
                raise ValidationError(_("Invalid new IBAN in mandate bank account history."))
