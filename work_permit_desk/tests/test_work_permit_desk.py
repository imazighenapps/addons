# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWorkPermit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "WorkPermit Other Company"})
        cls.start = datetime(2026, 6, 1, 8, 0, 0)
        cls.end = datetime(2026, 6, 1, 17, 0, 0)

    def _permit(self, **values):
        defaults = {
            "name": "WorkPermit Job A",
            "contractor": "WorkPermit Contractor A",
            "area": "WorkPermit Area North",
            "work_type": "general",
            "start_on": self.start,
            "end_on": self.end,
            "company_id": self.env.company.id,
        }
        defaults.update(values)
        return self.env["work.permit"].create(defaults)

    def test_01_permit_defaults(self):
        permit = self._permit()
        self.assertEqual(permit.state, "draft")
        self.assertEqual(permit.company_id, self.env.company)
        self.assertFalse(permit.is_active_now)

    def test_02_authorise_and_close(self):
        permit = self._permit()
        self.assertTrue(permit.action_authorise())
        self.assertEqual(permit.state, "authorised")
        self.assertTrue(permit.action_close())
        self.assertEqual(permit.state, "closed")
        self.assertTrue(permit.closed_on)

    def test_03_authorise_only_from_draft(self):
        permit = self._permit()
        permit.action_authorise()
        with self.assertRaises(ValidationError):
            permit.action_authorise()

    def test_04_close_only_from_authorised(self):
        permit = self._permit(name="WorkPermit Job B")
        with self.assertRaises(ValidationError):
            permit.action_close()

    def test_05_cancel_rules(self):
        permit = self._permit(name="WorkPermit Job C")
        self.assertTrue(permit.action_cancel())
        self.assertEqual(permit.state, "cancelled")
        closed = self._permit(name="WorkPermit Job D")
        closed.action_authorise()
        closed.action_close()
        with self.assertRaises(ValidationError):
            closed.action_cancel()

    def test_06_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self._permit(start_on=self.end, end_on=self.start)

    def test_07_expired_flag(self):
        past = self._permit(
            name="WorkPermit Job E",
            start_on=datetime(2026, 1, 10, 8, 0, 0),
            end_on=datetime(2026, 1, 10, 17, 0, 0))
        past.invalidate_recordset()
        self.assertTrue(past.is_expired)

    def test_08_active_now_flag(self):
        now = fields.Datetime.now()
        active = self._permit(
            name="WorkPermit Job F",
            start_on=now - timedelta(hours=1),
            end_on=now + timedelta(hours=2))
        active.action_authorise()
        active.invalidate_recordset()
        self.assertTrue(active.is_active_now)

    def test_09_work_type_filter(self):
        hot = self._permit(name="WorkPermit Job G", work_type="hot")
        self._permit(name="WorkPermit Job H", work_type="general")
        found = self.env["work.permit"].search([
            ("work_type", "=", "hot"), ("name", "=", "WorkPermit Job G")])
        self.assertIn(hot, found)
        self.assertEqual(len(found), 1)

    def test_10_company_isolation(self):
        foreign = self.env["work.permit"].with_company(
            self.other_company).create({
            "name": "WorkPermit Foreign Job",
            "contractor": "WorkPermit Contractor Z",
            "area": "WorkPermit Area South",
            "work_type": "general",
            "start_on": self.start,
            "end_on": self.end,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._permit(name="WorkPermit Local Job")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
