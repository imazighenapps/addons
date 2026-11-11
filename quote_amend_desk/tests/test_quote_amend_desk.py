# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestQuoteRevise(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "QuoteRevise Other Company"})

    def _amendment(self, **values):
        defaults = {
            "quote_ref": "QuoteRevise Test Quote SX-101",
            "revision_no": 2,
            "reason": "QuoteRevise Test customer asked for 25 units.",
        }
        defaults.update(values)
        return self.env["quote.amendment"].create(defaults)

    def _line(self, amendment=None, **values):
        defaults = {
            "amendment_id": (amendment or self._amendment()).id,
            "field_label": "Quantity",
            "old_value": "20",
            "new_value": "25",
        }
        defaults.update(values)
        return self.env["quote.change.line"].create(defaults)

    def test_01_amendment_defaults(self):
        amendment = self._amendment()
        self.assertEqual(amendment.state, "draft")
        self.assertEqual(amendment.company_id, self.env.company)
        self.assertTrue(amendment.name.startswith("Rev "))
        self.assertEqual(amendment.change_count, 0)

    def test_02_submit_stamps_the_date(self):
        amendment = self._amendment()
        self.assertTrue(amendment.action_submit())
        self.assertEqual(amendment.state, "submitted")
        self.assertTrue(amendment.submitted_on)

    def test_03_approve_stamps_the_approver(self):
        amendment = self._amendment()
        amendment.action_submit()
        self.assertTrue(amendment.action_approve())
        self.assertEqual(amendment.state, "approved")
        self.assertEqual(amendment.approved_user_id, self.env.user)
        self.assertTrue(amendment.approved_on)

    def test_04_double_approval_is_refused(self):
        amendment = self._amendment()
        amendment.action_submit()
        amendment.action_approve()
        with self.assertRaises(UserError):
            amendment.action_approve()

    def test_05_reject_closes_the_amendment(self):
        amendment = self._amendment()
        amendment.action_submit()
        self.assertTrue(amendment.action_reject())
        self.assertEqual(amendment.state, "rejected")
        with self.assertRaises(UserError):
            amendment.action_approve()

    def test_06_revision_number_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._amendment(revision_no=0)
        with self.assertRaises(ValidationError):
            self._amendment(revision_no=-1)

    def test_07_change_must_record_a_difference(self):
        with self.assertRaises(ValidationError):
            self._line(old_value="25", new_value="25")
        line = self._line()
        self.assertEqual(line.new_value, "25")
        with self.assertRaises(ValidationError):
            self._line(field_label=False)

    def test_08_change_counter_and_approved_filter(self):
        amendment = self._amendment()
        self._line(amendment=amendment)
        self._line(amendment=amendment, field_label="Delivery Date")
        amendment.action_submit()
        amendment.action_approve()
        amendment.invalidate_recordset()
        self.assertEqual(amendment.change_count, 2)
        found = self.env["quote.amendment"].search([
            ("state", "=", "approved"),
            ("change_count", ">", 0)])
        self.assertIn(amendment, found)

    def test_09_company_isolation(self):
        foreign = self.env["quote.amendment"].with_company(
            self.other_company).sudo().create({
            "quote_ref": "QuoteRevise Test Quote SX-102",
            "revision_no": 1,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        line = self._line(amendment=foreign)
        self.assertEqual(line.company_id, self.other_company)
        local = self._amendment()
        self.assertEqual(local.company_id, self.env.company)
