# -*- coding: utf-8 -*-
import logging
from datetime import datetime, time, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PrivacyRule(models.Model):
    _name = "privacy.rule"
    _description = "Data Retention Rule"
    _order = "model_name, retention_days, id"

    name = fields.Char(required=True)
    model_name = fields.Char(
        required=True,
        help="Technical name of the target model, for example res.partner.")
    date_field = fields.Char(
        required=True, default="create_date",
        help="Date or datetime field used to measure the age of a record, "
             "for example create_date.")
    retention_days = fields.Integer(
        required=True,
        help="Number of days after which a record is considered expired.")
    action = fields.Selection(
        [("anonymize", "Anonymize"), ("archive", "Archive"),
         ("delete", "Delete")],
        default="anonymize", required=True,
        help="What to do with an expired record. A partner is never deleted.")
    field_list = fields.Text(
        help="Fields to anonymize, one per line. Empty means no field.")
    mask_char = fields.Char(
        default="*",
        help="Character repeated six times to build the anonymization mask.")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    note = fields.Text()

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "A retention rule with this name already exists in this company.")

    @api.constrains("model_name", "date_field")
    def _check_target_model(self):
        for rule in self:
            if not rule.model_name or not rule.date_field:
                continue
            try:
                model = self.env[rule.model_name]
            except Exception as error:
                raise ValidationError(_(
                    "The model \"%s\" does not exist.",
                    rule.model_name)) from error
            if rule.date_field not in model._fields:
                raise ValidationError(_(
                    "The field \"%s\" does not exist on the model \"%s\".",
                    rule.date_field, rule.model_name))
            if model._fields[rule.date_field].type not in ("date", "datetime"):
                raise ValidationError(_(
                    "The field \"%s\" of the model \"%s\" is not a date.",
                    rule.date_field, rule.model_name))

    @api.constrains("retention_days")
    def _check_retention_days(self):
        for rule in self:
            if rule.retention_days <= 0:
                raise ValidationError(_(
                    "The retention period must be at least one day."))

    def _get_field_names(self):
        """Field names listed in field_list, in declaration order."""
        self.ensure_one()
        names = []
        for line in (self.field_list or "").splitlines():
            name = line.strip()
            if name and name not in names:
                names.append(name)
        return names

    def _get_mask(self):
        self.ensure_one()
        return (self.mask_char or "*") * 6

    def _anonymize_record(self, record):
        """Mask the configured fields of one record, never delete it.

        Only stored char, text and html fields are written: an identifier,
        a date or a monetary amount is not personal data per se and must
        stay usable for the accounting of the company.
        """
        self.ensure_one()
        values = {}
        for name in self._get_field_names():
            field = record._fields.get(name)
            if not field or not field.store or field.compute:
                continue
            if field.type not in ("char", "text", "html"):
                continue
            values[name] = self._get_mask()
        if values:
            record.write(values)
        return list(values)

    def _get_expired_records(self):
        """Records older than retention_days, filtered on the company."""
        self.ensure_one()
        try:
            model = self.env[self.model_name]
        except Exception:
            _logger.warning(
                "Retention rule %s targets an unknown model %r",
                self.name, self.model_name)
            return self.env["privacy.rule"].browse()
        fields_map = model._fields
        if self.date_field not in fields_map:
            return model.browse()
        date_field = fields_map[self.date_field]
        if date_field.type not in ("date", "datetime"):
            return model.browse()
        try:
            limit_date = fields.Date.context_today(self) - timedelta(
                days=self.retention_days or 0)
            limit_value = limit_date
            if date_field.type == "datetime":
                limit_value = datetime.combine(limit_date, time.min)
            domain = [(self.date_field, "<", limit_value)]
            if self.company_id and "company_id" in fields_map:
                # Shared records (no company) belong to every company.
                domain += ["|", ("company_id", "=", False),
                           ("company_id", "=", self.company_id.id)]
            return model.search(domain)
        except Exception:
            _logger.warning(
                "Unable to scan the expired records of %s with rule %s",
                self.model_name, self.name, exc_info=True)
            return model.browse()

    def _apply_retention(self, records):
        """Apply the rule action to an expired recordset, return the count."""
        self.ensure_one()
        if not records:
            return 0
        if self.action == "delete" and self.model_name != "res.partner":
            count = len(records)
            try:
                records.unlink()
                return count
            except Exception:
                _logger.warning(
                    "Could not delete the expired records of %s",
                    self.model_name, exc_info=True)
                return 0
        if self.action == "archive":
            try:
                model = self.env[self.model_name]
            except Exception:
                return 0
            if "active" not in model._fields:
                return 0
            try:
                records.write({"active": False})
                return len(records)
            except Exception:
                _logger.warning(
                    "Could not archive the expired records of %s",
                    self.model_name, exc_info=True)
                return 0
        count = 0
        for record in records:
            if self._anonymize_record(record):
                count += 1
        return count


class PrivacyRequest(models.Model):
    _name = "privacy.request"
    _description = "Data Subject Request"
    _inherit = ["mail.thread"]
    _order = "date_request desc, id desc"

    name = fields.Char(default="GDPR Request", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Data Subject", required=True,
        tracking=True, index=True)
    request_type = fields.Selection(
        [("access", "Access"), ("erasure", "Erasure"),
         ("rectification", "Rectification"), ("portability", "Portability")],
        default="access", required=True, tracking=True)
    date_request = fields.Date(
        default=fields.Date.context_today, required=True, tracking=True)
    date_deadline = fields.Date(
        string="Deadline", compute="_compute_date_deadline", store=True,
        help="Legal deadline: thirty days after the request date.")
    state = fields.Selection(
        [("new", "New"), ("in_progress", "In Progress"),
         ("done", "Done"), ("refused", "Refused")],
        default="new", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    handled_by_id = fields.Many2one(
        "res.users", string="Handled By", tracking=True)
    resolution_note = fields.Text()
    rule_ids = fields.Many2many(
        "privacy.rule", string="Applied Rules",
        help="Retention rules applied to this request. Empty means every "
             "active anonymization rule of res.partner.")
    active = fields.Boolean(default=True)

    @api.depends("date_request")
    def _compute_date_deadline(self):
        for request in self:
            if request.date_request:
                request.date_deadline = request.date_request + timedelta(
                    days=30)
            else:
                request.date_deadline = False

    def _get_partner_rules(self):
        """Anonymization rules of res.partner to apply on the data subject."""
        self.ensure_one()
        rules = self.rule_ids or self.env["privacy.rule"].search([
            ("action", "=", "anonymize"),
            ("model_name", "=", "res.partner"),
        ])
        return rules.filtered(
            lambda rule: rule.action == "anonymize"
            and rule.model_name == "res.partner")

    def action_start(self):
        for request in self:
            if request.state in ("done", "refused"):
                raise UserError(_(
                    "The request \"%s\" is already closed.", request.name))
            request.write({
                "state": "in_progress",
                "handled_by_id": self.env.user.id,
            })
            request.message_post(body=_(
                "Request set in progress, deadline %s.",
                request.date_deadline))
        return True

    def action_done(self):
        for request in self:
            if request.state == "refused":
                raise UserError(_(
                    "The refused request \"%s\" cannot be marked as done.",
                    request.name))
            request.write({
                "state": "done",
                "handled_by_id": self.env.user.id,
            })
            request.message_post(body=_("Request closed as done."))
        return True

    def action_refuse(self):
        for request in self:
            if request.state == "done":
                raise UserError(_(
                    "The request \"%s\" is done and cannot be refused.",
                    request.name))
            request.write({
                "state": "refused",
                "handled_by_id": self.env.user.id,
            })
            request.message_post(body=_(
                "Request refused. Reason: %s",
                request.resolution_note or _("not documented")))
        return True

    def action_anonymize_partner(self):
        for request in self:
            if not request.partner_id:
                raise UserError(_("The request has no data subject."))
            rules = request._get_partner_rules()
            if not rules:
                raise UserError(_(
                    "No active anonymization rule targets res.partner.\n"
                    "Create one in Privacy > Retention Rules first."))
            masked = []
            for rule in rules:
                masked += rule._anonymize_record(request.partner_id)
            masked = sorted(set(masked))
            note = request.resolution_note or _(
                "Personal data masked on %(count)s field(s): %(fields)s.",
                count=len(masked), fields=", ".join(masked))
            request.write({
                "state": "done",
                "handled_by_id": self.env.user.id,
                "resolution_note": note,
            })
            request.message_post(body=_(
                "Partner \"%s\" anonymized: %s field(s) masked, no record "
                "deleted.", request.partner_id.display_name, len(masked)))
        return True


class PrivacyScan(models.TransientModel):
    _name = "privacy.scan"
    _description = "Expired Data Scan"

    rule_ids = fields.Many2many(
        "privacy.rule", string="Rules",
        help="Rules to scan. Empty means every active rule.")
    dry_run = fields.Boolean(
        default=True,
        help="Only count the expired records. Uncheck to apply the actions.")

    def _notify(self, title, message, level="success"):
        """Push a notification without returning an action."""
        try:
            self.env["bus.bus"]._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {"type": level, "title": title, "message": message,
                 "sticky": False},
            )
        except Exception:
            _logger.debug("Unable to push the scan notification", exc_info=True)

    def action_scan(self):
        self.ensure_one()
        rules = self.rule_ids or self.env["privacy.rule"].search([])
        expired = 0
        updated = 0
        for rule in rules:
            records = rule._get_expired_records()
            expired += len(records)
            if self.dry_run or not records:
                continue
            updated += rule._apply_retention(records)
        if self.dry_run:
            message = _(
                "Dry run: %(count)s expired record(s) found by %(rules)s "
                "rule(s). Nothing was modified.",
                count=expired, rules=len(rules))
            level = "info"
        else:
            message = _(
                "%(count)s expired record(s) found, %(updated)s record(s) "
                "updated by %(rules)s rule(s).",
                count=expired, updated=updated, rules=len(rules))
            level = "warning" if updated else "success"
        self._notify(_("Privacy scan finished"), message, level)
        return True
