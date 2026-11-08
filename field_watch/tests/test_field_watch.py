# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFieldWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "FieldWatch Subject", "is_company": True})

    def _field(self, model, name):
        record = self.env["ir.model.fields"].search([
            ("model", "=", model), ("name", "=", name)], limit=1)
        self.assertTrue(record, "missing field %s.%s" % (model, name))
        return record

    def _message(self, model, res_id, when=datetime(2099, 3, 1, 10, 0)):
        return self.env["mail.message"].create({
            "model": model,
            "res_id": res_id,
            "message_type": "notification",
            "body": "FieldWatch test message",
            "date": when,
        })

    def _tracking(self, message, model, field_name, old, new,
                  kind="char"):
        values = {
            "mail_message_id": message.id,
            "field_id": self._field(model, field_name).id,
            "old_value_%s" % kind: old,
            "new_value_%s" % kind: new,
        }
        return self.env["mail.tracking.value"].create(values)

    def _rule(self, model, fields="", **kwargs):
        values = {
            "name": "FieldWatch Rule",
            "model_id": self.env["ir.model"].search(
                [("model", "=", model)], limit=1).id,
            "field_names": fields,
        }
        values.update(kwargs)
        return self.env["field.watch.rule"].create(values)

    def _collect(self, **kwargs):
        values = {
            "date_from": datetime(2099, 1, 1, 0, 0),
            "date_to": datetime(2099, 12, 31, 23, 59),
        }
        values.update(kwargs)
        wizard = self.env["field.watch.collect"].create(values)
        wizard.action_collect()
        return self.env["field.watch.log"].search([
            ("changed_date", ">=", datetime(2099, 1, 1, 0, 0)),
            ("changed_date", "<=", datetime(2099, 12, 31, 23, 59)),
        ])

    def test_01_collects_a_char_change(self):
        self._rule("res.partner")
        message = self._message("res.partner", self.partner.id)
        self._tracking(message, "res.partner", "name", "Old", "New")
        logs = self._collect()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.old_value, "Old")
        self.assertEqual(logs.new_value, "New")
        self.assertEqual(logs.field_name, "name")

    def test_02_collects_an_integer_change(self):
        self._rule("product.template")
        product = self.env["product.template"].create({
            "name": "FieldWatch Product"})
        message = self._message("product.template", product.id)
        self._tracking(message, "product.template", "sequence", 1, 9,
                       kind="integer")
        logs = self._collect()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.old_value, "1")
        self.assertEqual(logs.new_value, "9")

    def test_03_second_collection_does_not_duplicate(self):
        self._rule("res.partner")
        message = self._message("res.partner", self.partner.id)
        self._tracking(message, "res.partner", "name", "Old", "New")
        first = len(self._collect())
        second = len(self._collect())
        self.assertEqual(first, second)

    def test_04_rule_restricts_the_fields(self):
        self._rule("res.partner", fields="name")
        message = self._message("res.partner", self.partner.id)
        self._tracking(message, "res.partner", "email",
                       "old@example.com", "new@example.com")
        self.assertFalse(self._collect())

    def test_05_period_filter(self):
        self._rule("res.partner")
        message = self._message("res.partner", self.partner.id,
                                when=datetime(2000, 1, 1, 10, 0))
        self._tracking(message, "res.partner", "name", "Old", "New")
        self.assertFalse(self._collect())

    def test_06_review_ignore_reopen(self):
        self._rule("res.partner")
        message = self._message("res.partner", self.partner.id)
        self._tracking(message, "res.partner", "name", "Old", "New")
        log = self._collect()
        self.assertTrue(log.action_review())
        self.assertEqual(log.state, "reviewed")
        self.assertTrue(log.action_ignore())
        self.assertEqual(log.state, "ignored")
        self.assertTrue(log.action_reopen())
        self.assertEqual(log.state, "new")

    def test_07_empty_field_list_watches_everything(self):
        rule = self._rule("res.partner", fields="")
        self.assertTrue(rule._matches("res.partner", "name"))
        self.assertTrue(rule._matches("res.partner", "email"))
        self.assertFalse(rule._matches("product.template", "name"))
        narrowed = self._rule("res.partner", fields="name",
                              name="FieldWatch Narrow")
        self.assertTrue(narrowed._matches("res.partner", "name"))
        self.assertFalse(narrowed._matches("res.partner", "email"))

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "FieldWatch Other Company"})
        self._rule("res.partner", company_id=other.id)
        message = self._message("res.partner", self.partner.id)
        self._tracking(message, "res.partner", "name", "Old", "New")
        self.assertFalse(self._collect())
        self._rule("res.partner", name="FieldWatch Mine")
        logs = self._collect()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.company_id, self.env.company)
