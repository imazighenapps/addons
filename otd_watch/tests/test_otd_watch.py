# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOnTime(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "OnTime Other Company"})

    def _commitment(self, promised=None, **values):
        defaults = {
            "order_ref": "OnTime Test Order SO-3020",
            "customer_name": "OnTime Test Customer",
            "promised_on": promised or "2026-10-06",
        }
        defaults.update(values)
        return self.env["otd.commitment"].create(defaults)

    def test_01_commitment_defaults(self):
        commitment = self._commitment()
        self.assertEqual(commitment.state, "open")
        self.assertEqual(commitment.company_id, self.env.company)
        self.assertTrue(commitment.name.startswith("Ship "))
        self.assertFalse(commitment.on_time)
        self.assertEqual(commitment.delay_days, 0)

    def test_02_early_shipment_is_on_time(self):
        commitment = self._commitment()
        commitment.write({"shipped_on": "2026-10-02"})
        self.assertTrue(commitment.on_time)
        self.assertEqual(commitment.delay_days, -4)

    def test_03_late_shipment_counted_in_days(self):
        commitment = self._commitment()
        commitment.write({"shipped_on": "2026-10-09"})
        self.assertFalse(commitment.on_time)
        self.assertEqual(commitment.delay_days, 3)

    def test_04_ship_today_stamps_and_scores(self):
        commitment = self._commitment()
        self.assertTrue(commitment.action_ship_today())
        self.assertEqual(commitment.state, "shipped")
        self.assertTrue(commitment.shipped_on)
        self.assertEqual(commitment.delay_days,
                         (commitment.shipped_on
                          - commitment.promised_on).days)

    def test_05_double_shipment_is_refused(self):
        commitment = self._commitment()
        commitment.action_ship_today()
        with self.assertRaises(UserError):
            commitment.action_ship_today()

    def test_06_score_works_both_ways(self):
        early = self._commitment(order_ref="OnTime Test Order SO-3021",
                                 promised="2026-10-06")
        early.write({"shipped_on": "2026-10-06"})
        self.assertTrue(early.on_time)
        self.assertEqual(early.delay_days, 0)
        late = self._commitment(order_ref="OnTime Test Order SO-3022",
                                promised="2026-10-06")
        late.write({"shipped_on": "2026-10-13"})
        self.assertFalse(late.on_time)
        self.assertEqual(late.delay_days, 7)

    def test_07_reopen_clears_the_score(self):
        commitment = self._commitment()
        commitment.action_ship_today()
        self.assertTrue(commitment.action_back_to_open())
        self.assertEqual(commitment.state, "open")
        self.assertFalse(commitment.shipped_on)
        self.assertEqual(commitment.delay_days, 0)
        with self.assertRaises(UserError):
            commitment.action_back_to_open()

    def test_08_filter_scores_late_shipments(self):
        late = self._commitment(order_ref="OnTime Test Order SO-3023",
                                promised="2026-11-03")
        late.write({"shipped_on": "2026-11-10"})
        on_time = self._commitment(order_ref="OnTime Test Order SO-3024",
                                   promised="2026-11-03")
        on_time.write({"shipped_on": "2026-11-03"})
        found = self.env["otd.commitment"].search([
            ("delay_days", ">", 0)])
        self.assertIn(late, found)
        self.assertNotIn(on_time, found)
        found = self.env["otd.commitment"].search([
            ("on_time", "=", True)])
        self.assertIn(on_time, found)
        self.assertNotIn(late, found)

    def test_09_company_isolation(self):
        foreign = self.env["otd.commitment"].with_company(
            self.other_company).sudo().create({
            "order_ref": "OnTime Test Order SO-3025",
            "customer_name": "OnTime Test Foreign Customer",
            "promised_on": "2026-10-06",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._commitment(
            order_ref="OnTime Test Order SO-3026")
        self.assertEqual(local.company_id, self.env.company)
