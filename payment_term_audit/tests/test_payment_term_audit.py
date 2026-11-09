# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTermAudit(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        line_fields = cls.env["account.payment.term.line"]._fields
        days_key = "nb_days" if "nb_days" in line_fields else "delay"
        cls.term30 = cls.env["account.payment.term"].create({
            "name": "Thirty days",
            "line_ids": [(0, 0, {days_key: 30})],
        })

    def _partner(self, term=None):
        return self.env["res.partner"].create({
            "name": "Term test partner",
            "property_payment_term_id": term.id if term else False,
        })

    def _invoice(self, partner, due_offset):
        invoice = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": partner.id,
            "invoice_date": date(2099, 1, 5),
            "invoice_line_ids": [(0, 0, {
                "quantity": 1.0,
                "price_unit": 120.0,
            })],
        })
        invoice.action_post()
        # Posting recomputes the due date from the payment term, so the
        # audited due date is written after the post, the way an edited
        # invoice behaves in production.
        invoice.write({
            "invoice_date_due": date(2099, 1, 5) + timedelta(days=due_offset),
        })
        return invoice

    def _audit(self):
        audit = self.env["payment.term.audit"].create({
            "name": "Audit 2099",
            "date_from": date(2099, 1, 1),
            "date_to": date(2099, 12, 31),
            "tolerance": 0,
        })
        audit.action_run()
        return audit

    def _post(self, invoice):
        invoice.action_post()

    def test_01_matching_terms_are_not_anomalies(self):
        invoice = self._invoice(self._partner(self.term30), 30)
        audit = self._audit()
        self.assertFalse(audit.line_ids.filtered(
            lambda line: line.move_id == invoice))

    def test_02_a_later_due_date_is_a_mismatch(self):
        invoice = self._invoice(self._partner(self.term30), 60)
        audit = self._audit()
        line = audit.line_ids.filtered(
            lambda item: item.move_id == invoice)
        self.assertTrue(line)
        self.assertEqual(line.kind, "mismatch")
        self.assertEqual(line.gap_days, 30)

    def test_03_a_partner_without_term_is_reported(self):
        invoice = self._invoice(self._partner(), 15)
        audit = self._audit()
        line = audit.line_ids.filtered(
            lambda item: item.move_id == invoice)
        self.assertTrue(line)
        self.assertEqual(line.kind, "missing_term")

    def test_04_running_twice_never_duplicates(self):
        self._invoice(self._partner(self.term30), 60)
        audit = self._audit()
        count = len(audit.line_ids)
        audit.action_run()
        self.assertEqual(len(audit.line_ids), count)

    def test_05_the_audit_counts_what_it_scanned(self):
        self._invoice(self._partner(self.term30), 60)
        audit = self._audit()
        audit.invalidate_recordset()
        self.assertEqual(audit.state, "done")
        self.assertGreaterEqual(audit.checked_count, 1)
        self.assertEqual(audit.anomaly_count, audit.checked_count)

    def test_06_an_anomaly_can_be_ignored_and_reopened(self):
        self._invoice(self._partner(self.term30), 60)
        audit = self._audit()
        line = audit.line_ids[0]
        line.action_ignore()
        self.assertEqual(line.state, "ignored")
        line.action_reopen()
        self.assertEqual(line.state, "new")

    def test_07_invoices_outside_the_window_are_ignored(self):
        invoice = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self._partner(self.term30).id,
            "invoice_date": date(1998, 1, 5),
            "invoice_line_ids": [(0, 0, {"quantity": 1.0,
                                         "price_unit": 80.0})],
        })
        self._post(invoice)
        invoice.write({"invoice_date_due": date(1998, 2, 4)})
        audit = self._audit()
        self.assertFalse(audit.line_ids.filtered(
            lambda line: line.move_id == invoice))

    def test_08_companies_are_isolated(self):
        other = self.env["res.company"].create({"name": "Term audit B"})
        self._invoice(self._partner(self.term30), 60)
        other_audit = self.env["payment.term.audit"].create({
            "name": "Audit other company",
            "date_from": date(2099, 1, 1),
            "date_to": date(2099, 12, 31),
            "tolerance": 0,
            "company_id": other.id,
        })
        other_audit.action_run()
        self.assertEqual(other_audit.state, "done")
        self.assertFalse(other_audit.line_ids)
