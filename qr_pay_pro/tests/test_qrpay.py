# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from ..models.qr_tools import (
    make_rf_reference, is_rf_reference, make_qrr_reference,
    is_qrr_reference, is_qr_iban, build_epc_payload, decode_epc_payload,
)


@tagged("post_install", "-at_install")
class TestQrTools(TransactionCase):
    def test_01_rf(self):
        ref = make_rf_reference("INV000123")
        self.assertTrue(ref.startswith("RF"))
        self.assertTrue(is_rf_reference(ref))
        self.assertFalse(is_rf_reference("RF00123"))
        self.assertFalse(make_rf_reference("bad ref!"))
        self.assertEqual(ref, "RF" + ref[2:4] + "INV000123")

    def test_02_qrr(self):
        ref = make_qrr_reference("123456")
        self.assertEqual(len(ref), 27)
        self.assertTrue(is_qrr_reference(ref))
        self.assertFalse(is_qrr_reference("123"))

    def test_03_qr_iban(self):
        self.assertTrue(is_qr_iban("CH443199912300088901"))
        self.assertFalse(is_qr_iban("CH9300762011623852957"))
        self.assertFalse(is_qr_iban("FR1420041010050500013M02606"))

    def test_04_epc(self):
        ok, payload = build_epc_payload(
            "Demo AG", "DE75512108001245126199", 12.30, "EUR",
            rf_reference="RF18539007547034")
        self.assertTrue(ok)
        lines = payload.split("\n")
        self.assertEqual(lines[0], "BCD")
        self.assertEqual(lines[9], "RF18539007547034")
        self.assertEqual(lines[10], "")
        ok, msg = build_epc_payload("D", "DE75512108001245126199", 1.0, "USD")
        self.assertFalse(ok)
        bad = build_epc_payload("D", "DE75512108001245126199", 1.0, "EUR",
                                rf_reference="RF18539007547034", remittance="hi")
        self.assertFalse(bad[0])
        decoded = decode_epc_payload(payload)
        self.assertEqual(decoded["iban"], "DE75512108001245126199")
        self.assertFalse(decode_epc_payload("hello"))


@tagged("post_install", "-at_install")
class TestQrPayMove(TransactionCase):
    def test_05_assign_and_validate(self):
        move = self.env["account.move"].create({"move_type": "out_invoice"})
        move.action_qr_pay_assign_rf()
        self.assertEqual(move.qr_pay_reference_type, "rf")
        self.assertTrue(is_rf_reference(move.qr_pay_reference))
        self.assertTrue(move.qr_pay_valid)
        move.write({"qr_pay_reference": "BOGUS", "qr_pay_reference_type": "rf"})
        self.assertFalse(move.qr_pay_valid)
        move.action_qr_pay_assign_qrr()
        self.assertEqual(len(move.qr_pay_reference), 27)
        self.assertTrue(move.qr_pay_valid)
