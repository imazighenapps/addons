# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLeaseDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "LeaseDesk Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "LeaseDesk Test Lessor"})

    def _lease(self, **values):
        defaults = {
            "name": "LeaseDesk Test Lease",
            "partner_id": self.partner.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 3, 1),
            "monthly_amount": 1000.0,
        }
        defaults.update(values)
        return self.env["lease.contract"].create(defaults)

    def test_01_lease_defaults(self):
        lease = self._lease(name="LeaseDesk Defaults")
        self.assertEqual(lease.state, "draft")
        self.assertEqual(lease.company_id, self.env.company)
        self.assertEqual(lease.schedule_count, 0)
        self.assertAlmostEqual(lease.posted_amount, 0.0, places=2)

    def test_02_generate_schedule(self):
        lease = self._lease(name="LeaseDesk Schedule")
        self.assertTrue(lease.action_generate_schedule())
        self.assertEqual(lease.schedule_count, 3)
        self.assertAlmostEqual(lease.remaining_amount, 3000.0, places=2)
        self.assertEqual(lease.line_ids[0].due_date, date(2026, 1, 1))

    def test_03_no_duplicate_schedule(self):
        lease = self._lease(name="LeaseDesk Duplicate")
        lease.action_generate_schedule()
        with self.assertRaises(UserError):
            lease.action_generate_schedule()

    def test_04_start_requires_schedule(self):
        lease = self._lease(name="LeaseDesk NoSched")
        with self.assertRaises(UserError):
            lease.action_start()
        lease.action_generate_schedule()
        self.assertTrue(lease.action_start())
        self.assertEqual(lease.state, "running")

    def test_05_post_line_and_totals(self):
        lease = self._lease(name="LeaseDesk Post")
        lease.action_generate_schedule()
        lease.action_start()
        line = lease.line_ids.sorted("due_date")[0]
        self.assertTrue(line.action_post())
        self.assertEqual(line.state, "posted")
        self.assertTrue(line.posted_on)
        lease.invalidate_recordset()
        self.assertAlmostEqual(lease.posted_amount, 1000.0, places=2)
        self.assertAlmostEqual(lease.remaining_amount, 2000.0, places=2)

    def test_06_close_workflow_and_locks(self):
        lease = self._lease(name="LeaseDesk Close")
        lease.action_generate_schedule()
        with self.assertRaises(UserError):
            lease.action_close()
        lease.action_start()
        self.assertTrue(lease.action_close())
        self.assertEqual(lease.state, "closed")
        with self.assertRaises(UserError):
            self.env["lease.schedule"].create({
                "lease_id": lease.id,
                "sequence": 99,
                "due_date": date(2026, 4, 1),
                "amount": 1000.0,
            })

    def test_07_constraints(self):
        with self.assertRaises(ValidationError):
            self._lease(name="LeaseDesk Bad Dates",
                        date_start=date(2026, 6, 1),
                        date_end=date(2026, 1, 1))
        with self.assertRaises(ValidationError):
            self._lease(name="LeaseDesk Zero", monthly_amount=0.0)
        lease = self._lease(name="LeaseDesk Bad Line")
        lease.action_generate_schedule()
        with self.assertRaises(ValidationError):
            lease.line_ids[0].write({"amount": -1.0})

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
            "name": "LeaseDesk Foreign Lessor"})
        foreign = self.env["lease.contract"].with_company(
            self.other_company).sudo().create({
            "name": "LeaseDesk Foreign",
            "partner_id": foreign_partner.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 2, 1),
            "monthly_amount": 500.0,
            "company_id": self.other_company.id,
        })
        local = self._lease(name="LeaseDesk Local")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
