# -*- coding: utf-8 -*-
from odoo import fields, models, _


class FieldWatchCollect(models.TransientModel):
    _name = "field.watch.collect"
    _description = "Collect Field Changes"

    date_from = fields.Datetime(required=True)
    date_to = fields.Datetime(required=True)
    model_ids = fields.Many2many("ir.model", string="Models")
    rule_ids = fields.Many2many("field.watch.rule", string="Rules")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)

    def _value(self, tracking, prefix):
        for suffix in ("char", "text", "integer", "float", "datetime"):
            name = "%s_value_%s" % (prefix, suffix)
            if name not in tracking._fields:
                continue
            value = tracking[name]
            # Only the suffix matching the tracked field type is filled; the
            # others stay False. 0 and 0.0 are real values and must survive.
            if value is None or value is False or value == "":
                continue
            return str(value)
        return ""

    def _rules(self):
        domain = [
            ("active", "=", True),
            "|", ("company_id", "=", False),
            ("company_id", "=", self.company_id.id),
        ]
        if self.rule_ids:
            domain = [("id", "in", self.rule_ids.ids)]
        elif self.model_ids:
            domain.append(("model_id", "in", self.model_ids.ids))
        return self.env["field.watch.rule"].search(domain)

    def action_collect(self):
        self.ensure_one()
        rules = self._rules()
        if not rules:
            return True
        Tracking = self.env["mail.tracking.value"].search([
            ("mail_message_id.date", ">=", self.date_from),
            ("mail_message_id.date", "<=", self.date_to),
        ], order="id")
        Log = self.env["field.watch.log"]
        created = Log
        for tracking in Tracking:
            message = tracking.mail_message_id
            if not message.model or not tracking.field_id:
                continue
            rule = rules.filtered(
                lambda r: r._matches(message.model, tracking.field_id.name))[:1]
            if not rule:
                continue
            if Log.search_count([
                    ("message_id", "=", message.id),
                    ("field_name", "=", tracking.field_id.name)]):
                continue
            record_name = False
            try:
                record = self.env[message.model].browse(message.res_id)
                record_name = record.display_name
            except (KeyError, ValueError):
                record_name = False
            created |= Log.create({
                "rule_id": rule.id,
                "model_id": rule.model_id.id,
                "res_id": message.res_id,
                "record_name": record_name or False,
                "field_name": tracking.field_id.name,
                "field_label": tracking.field_id.field_description,
                "old_value": self._value(tracking, "old"),
                "new_value": self._value(tracking, "new"),
                "changed_by_id": message.author_id.id or False,
                "changed_date": message.date,
                "company_id": self.company_id.id,
                "message_id": message.id,
            })
        action = {
            "type": "ir.actions.act_window",
            "name": _("Change Log"),
            "res_model": "field.watch.log",
            "view_mode": "list,form",
        }
        if created:
            action["domain"] = [("id", "in", created.ids)]
        else:
            action["domain"] = [
                ("company_id", "=", self.company_id.id),
                ("state", "=", "new"),
            ]
        return action
