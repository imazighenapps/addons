# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPalletDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({"name": "PalletDesk Other Company"})
        cls.account = cls.env["pallet.account"].create({
            "name": "PalletDesk Account Alpha",
            "partner_name": "PalletDesk Partner Alpha",
        })

    def _movement(self, account=None, **vals):
        data = {
            "name": "PM-TEST-001",
            "account_id": (account or self.account).id,
            "direction": "lent",
            "quantity": 5,
            "movement_date": "2026-02-10",
            "reference": "DN-001",
        }
        data.update(vals)
        return self.env["pallet.movement"].create(data)

    def test_01_account_defaults(self):
        self.assertEqual(self.account.company_id, self.env.company)
        self.assertEqual(self.account.lent_qty, 0)
        self.assertEqual(self.account.returned_qty, 0)
        self.assertEqual(self.account.balance_qty, 0)

    def test_02_movement_defaults(self):
        move = self._movement(name="PM-DEF-2026")
        self.assertEqual(move.state, "draft")
        self.assertFalse(move.confirmed_on)
        self.assertEqual(move.partner_name, "PalletDesk Partner Alpha")

    def test_03_confirm_updates_balance(self):
        lent = self._movement(name="PM-LENT-2026", quantity=8, movement_date="2026-03-01")
        lent.action_confirm()
        self.account.invalidate_recordset()
        self.assertEqual(self.account.lent_qty, 8)
        self.assertEqual(self.account.balance_qty, 8)
        ret = self._movement(name="PM-RET-2026", direction="returned", quantity=3, movement_date="2026-03-02")
        ret.action_confirm()
        self.account.invalidate_recordset()
        self.assertEqual(self.account.returned_qty, 3)
        self.assertEqual(self.account.balance_qty, 5)

    def test_04_reset_updates_balance(self):
        move = self._movement(name="PM-RST-2026", quantity=4, movement_date="2026-03-10")
        move.action_confirm()
        self.account.invalidate_recordset()
        self.assertEqual(self.account.balance_qty, 4)
        move.action_reset()
        self.account.invalidate_recordset()
        self.assertEqual(self.account.balance_qty, 0)
        self.assertEqual(move.state, "draft")

    def test_05_invalid_transitions(self):
        move = self._movement(name="PM-INV-2026", movement_date="2026-04-01")
        with self.assertRaises(UserError):
            move.action_reset()
        move.action_confirm()
        with self.assertRaises(UserError):
            move.action_confirm()

    def test_06_quantity_constraint(self):
        with self.assertRaises(ValidationError):
            self._movement(name="PM-QTY-2026", movement_date="2026-05-01", quantity=0)

    def test_07_account_unique_partner(self):
        with self.assertRaises(ValidationError):
            self.env["pallet.account"].create({
                "name": "PalletDesk Account Alpha Duplicate",
                "partner_name": "PalletDesk Partner Alpha",
            })

    def test_08_movement_count(self):
        self._movement(name="PM-CNT-A-2026", movement_date="2026-06-01")
        self._movement(name="PM-CNT-B-2026", movement_date="2026-06-02", direction="returned", quantity=1)
        self.account.invalidate_recordset()
        self.assertEqual(self.account.movement_count, 2)

    def test_09_multi_company_isolation(self):
        foreign_account = self.env["pallet.account"].with_company(self.other_company).create({
            "name": "PalletDesk Foreign Account",
            "partner_name": "PalletDesk Foreign Partner",
            "company_id": self.other_company.id,
        })
        foreign_move = self.env["pallet.movement"].with_company(self.other_company).create({
            "name": "PM-MC-OTH-2026",
            "account_id": foreign_account.id,
            "direction": "lent",
            "quantity": 7,
            "movement_date": "2026-07-01",
            "company_id": self.other_company.id,
        })
        self.assertEqual(self.account.company_id, self.env.company)
        self.assertEqual(foreign_account.company_id, self.other_company)
        self.assertNotEqual(self.account.company_id, foreign_move.company_id)
        foreign_move.action_confirm()
        foreign_account.invalidate_recordset()
        self.assertEqual(foreign_account.balance_qty, 7)
