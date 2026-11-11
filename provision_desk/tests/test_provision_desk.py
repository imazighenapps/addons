# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProvisionDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ProvisionDesk Other Company"})
        cls.provision = cls.env["provision.book"].create({
            "name": "ProvisionDesk Test Bad Debt",
            "provision_type": "bad_debt",
            "opening_balance": 1000.0,
        })

    def _move(self, provision=None, **values):
        defaults = {
            "provision_id": (provision or self.provision).id,
            "date": date(2026, 2, 15),
            "movement_type": "increase",
            "amount": 200.0,
            "reason": "ProvisionDesk Test Movement",
        }
        defaults.update(values)
        return self.env["provision.movement"].create(defaults)

    def test_01_provision_defaults(self):
        prov = self.env["provision.book"].create({
            "name": "ProvisionDesk Defaults",
            "provision_type": "warranty",
        })
        self.assertEqual(prov.state, "open")
        self.assertEqual(prov.company_id, self.env.company)
        self.assertEqual(prov.opening_balance, 0.0)
        self.assertEqual(prov.current_balance, 0.0)

    def test_02_balance_from_movements(self):
        self._move(amount=300.0, movement_type="increase",
                   reason="ProvisionDesk Increase")
        self._move(amount=100.0, movement_type="decrease",
                   reason="ProvisionDesk Decrease", date=date(2026, 3, 1))
        self.provision.invalidate_recordset()
        self.assertAlmostEqual(self.provision.current_balance, 1200.0, places=2)
        self.assertEqual(self.provision.movement_count, 2)

    def test_03_opening_balance_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["provision.book"].create({
                "name": "ProvisionDesk Negative",
                "opening_balance": -10.0,
            })

    def test_04_movement_amount_constraint(self):
        with self.assertRaises(ValidationError):
            self._move(amount=0.0, reason="ProvisionDesk Zero")
        with self.assertRaises(ValidationError):
            self._move(amount=-5.0, reason="ProvisionDesk Negative")

    def test_05_close_and_reopen(self):
        self.assertTrue(self.provision.action_close())
        self.assertEqual(self.provision.state, "closed")
        with self.assertRaises(UserError):
            self.provision.action_close()
        self.assertTrue(self.provision.action_reopen())
        self.assertEqual(self.provision.state, "open")
        with self.assertRaises(UserError):
            self.provision.action_reopen()

    def test_06_closed_provision_blocks_movements(self):
        self.provision.action_close()
        with self.assertRaises(UserError):
            self._move(reason="ProvisionDesk Blocked")
        move = self.env["provision.movement"].create({
            "provision_id": self.env["provision.book"].create({
                "name": "ProvisionDesk Temp",
            }).id,
            "date": date(2026, 4, 1),
            "movement_type": "increase",
            "amount": 50.0,
            "reason": "ProvisionDesk Temp Move",
        })
        move.provision_id.action_close()
        with self.assertRaises(UserError):
            move.write({"amount": 60.0})

    def test_07_balance_multiple_movements(self):
        prov = self.env["provision.book"].create({
            "name": "ProvisionDesk Multi",
            "opening_balance": 500.0,
        })
        self._move(provision=prov, amount=250.0, movement_type="increase",
                   reason="ProvisionDesk M1")
        self._move(provision=prov, amount=150.0, movement_type="increase",
                   reason="ProvisionDesk M2", date=date(2026, 3, 10))
        self._move(provision=prov, amount=100.0, movement_type="decrease",
                   reason="ProvisionDesk M3", date=date(2026, 4, 10))
        prov.invalidate_recordset()
        self.assertAlmostEqual(prov.current_balance, 800.0, places=2)
        self.assertEqual(prov.movement_count, 3)

    def test_08_company_isolation(self):
        foreign = self.env["provision.book"].with_company(
            self.other_company).sudo().create({
            "name": "ProvisionDesk Foreign",
            "provision_type": "other",
            "opening_balance": 100.0,
            "company_id": self.other_company.id,
        })
        local = self.env["provision.book"].create({
            "name": "ProvisionDesk Local",
            "provision_type": "warranty",
            "opening_balance": 200.0,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
