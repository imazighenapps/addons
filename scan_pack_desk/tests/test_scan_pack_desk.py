# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestScanPackDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.product"].create({
            "name": "ScanPack Test Widget",
            "barcode": "4000000000001",
            "default_code": "SCAN-A",
        })
        cls.product_b = cls.env["product.product"].create({
            "name": "ScanPack Test Gizmo",
            "barcode": "4000000000002",
            "default_code": "SCAN-B",
        })
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.picking = cls.env["stock.picking"].create({
            "picking_type_id": cls.picking_type.id,
            "location_id": cls.picking_type.default_location_src_id.id,
            "location_dest_id":
                cls.picking_type.default_location_dest_id.id,
        })
        cls._move(cls.product_a, 2.0)
        cls._move(cls.product_b, 3.0)
        cls.picking.action_confirm()
        cls.picking.action_open_scan_session()
        cls.session = cls.env["scan_pack.session"].search(
            [("picking_id", "=", cls.picking.id)])
        cls.manager = cls._user(
            "scanpack-test-manager",
            ["stock.group_stock_manager",
             "scan_pack_desk.group_scanpackdesk_user"])
        cls.outsider = cls._user(
            "scanpack-test-outsider", ["base.group_user"])

    @classmethod
    def _move(cls, product, qty):
        """A pick move, with the version differences of stock.move.name."""
        values = {
            "picking_id": cls.picking.id,
            "product_id": product.id,
            "product_uom_qty": qty,
            "picking_type_id": cls.picking_type.id,
            "location_id": cls.picking_type.default_location_src_id.id,
            "location_dest_id":
                cls.picking_type.default_location_dest_id.id,
        }
        if "name" in cls.env["stock.move"]._fields:
            values["name"] = product.display_name
        return cls.env["stock.move"].create(values)

    @classmethod
    def _user(cls, login, group_refs):
        """A test user: groups_id in 18.0, group_ids in 19.0 and 20.0."""
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields \
            else "groups_id"
        return cls.env["res.users"].create({
            "name": login.title(),
            "login": login,
            field: [(6, 0, groups)],
        })

    def _scan(self, session, barcode):
        session.scan_code = barcode
        session.action_scan()

    def _line(self, product):
        return self.session.move_ids.filtered(
            lambda line: line.product_id == product)

    def test_01_scan_increments_the_right_line(self):
        self.assertEqual(len(self.session.move_ids), 2)
        self._scan(self.session, "4000000000001")
        self.assertAlmostEqual(self._line(self.product_a).scanned_qty, 1.0)
        self.assertAlmostEqual(self._line(self.product_b).scanned_qty, 0.0)
        self._scan(self.session, "SCAN-A")
        self.assertAlmostEqual(self._line(self.product_a).scanned_qty, 2.0)
        self.assertAlmostEqual(self.session.scanned_qty, 2.0)
        self.assertAlmostEqual(self.session.demand_qty, 5.0)
        self.assertFalse(self.session.scan_code)
        self.assertEqual(self.session.last_result, "accepted")
        accepted = self.session.log_ids.filtered(
            lambda entry: entry.result == "accepted")
        self.assertEqual(len(accepted), 2)
        self.assertEqual(accepted[0].product_id, self.product_a)
        self.assertAlmostEqual(accepted[0].qty, 1.0)

    def test_02_unexpected_barcode_is_refused_and_logged(self):
        self._scan(self.session, "4000999999999")
        self.assertAlmostEqual(self.session.scanned_qty, 0.0)
        self.assertEqual(self.session.last_result, "unknown")
        unknown = self.session.log_ids.filtered(
            lambda entry: entry.result == "unknown")
        self.assertEqual(len(unknown), 1)
        self._scan(self.session, "4000000000003")
        still_unknown = self.session.log_ids.filtered(
            lambda entry: entry.result == "unknown")
        self.assertEqual(len(still_unknown), 2)
        self._scan(self.session, "4000000000001")
        self._scan(self.session, "4000000000001")
        self.assertTrue(self._line(self.product_a).is_complete)
        self._scan(self.session, "4000000000001")
        excess = self.session.log_ids.filtered(
            lambda entry: entry.result == "excess")
        self.assertEqual(len(excess), 1)
        self.assertAlmostEqual(self._line(self.product_a).scanned_qty, 2.0)

    def test_03_validation_blocked_until_balanced(self):
        with self.assertRaises(UserError):
            self.picking.button_validate()
        self._scan(self.session, "4000000000001")
        self._scan(self.session, "4000000000001")
        self._scan(self.session, "4000000000002")
        self._scan(self.session, "4000000000002")
        with self.assertRaises(UserError):
            self.picking.button_validate()
        self.assertFalse(self.session.has_exception)
        self._scan(self.session, "4000000000002")
        self.assertTrue(self.session.is_balanced)
        self.assertTrue(self.picking.button_validate())
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(self.session.state, "validated")
        self.assertTrue(self.session.validated_at)
        validated = self.session.log_ids.filtered(
            lambda entry: entry.result == "validated")
        self.assertEqual(len(validated), 1)

    def test_04_exception_requires_reason_and_is_journaled(self):
        self._scan(self.session, "4000000000001")
        self._scan(self.session, "4000000000001")
        with self.assertRaises(UserError):
            self.picking.button_validate()
        with self.assertRaises(UserError):
            self.session.action_grant_exception()
        self.session.exception_reason = "Box damaged, 3 gizmos missing"
        with self.assertRaises(UserError):
            self.session.with_user(self.outsider).action_grant_exception()
        self.session.with_user(self.manager).action_grant_exception()
        self.assertTrue(self.session.has_exception)
        self.assertEqual(self.session.exception_by_id, self.manager)
        exceptions = self.session.log_ids.filtered(
            lambda entry: entry.result == "exception")
        self.assertEqual(len(exceptions), 1)
        self.assertIn("Box damaged", exceptions[0].message)
        self.assertTrue(self.picking.button_validate())
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(self.session.state, "validated")

    def test_05_session_and_journal_are_locked_after_validation(self):
        self._scan(self.session, "4000000000001")
        self.session.exception_reason = "Short by two widgets, shipped demo"
        self.session.with_user(self.manager).action_grant_exception()
        self.assertTrue(self.picking.button_validate())
        with self.assertRaises(UserError):
            self._scan(self.session, "4000000000001")
        with self.assertRaises(UserError):
            self.session.write({"scan_qty": 2.0})
        with self.assertRaises(UserError):
            self.session.log_ids[0].write({"message": "tampered"})
        with self.assertRaises(UserError):
            self.session.log_ids[0].unlink()

    def test_06_constraints(self):
        with self.assertRaises(ValidationError):
            self.session.write({"scan_qty": 0.0})
        line = self.session.move_ids[0]
        with self.assertRaises(ValidationError):
            line.write({"scanned_qty": -1.0})
        with self.assertRaises(ValidationError):
            self.env["scan_pack.move"].create({
                "session_id": self.session.id,
                "move_id": line.move_id.id,
            })
        with self.assertRaises(ValidationError):
            self.env["scan_pack.session"].create({
                "picking_id": self.picking.id,
            })

    def test_07_journal_is_immutable(self):
        self._scan(self.session, "4000000000001")
        entry = self.session.log_ids[0]
        self.assertEqual(entry.user_id, self.env.user)
        self.assertTrue(entry.barcode)
        with self.assertRaises(UserError):
            entry.write({"qty": 99.0})
        with self.assertRaises(UserError):
            entry.unlink()

    def test_08_journal_is_company_isolated(self):
        company_b = self.env["res.company"].create({
            "name": "ScanPack Test B",
        })
        self._scan(self.session, "4000000000001")
        foreign = self.env["scan_pack.log"].create({
            "session_id": self.session.id,
            "company_id": company_b.id,
            "user_id": self.env.user.id,
            "qty": 0.0,
            "result": "unknown",
            "message": "Foreign company entry",
        })
        # The superuser bypasses record rules: search as a real user.
        visible = self.env["scan_pack.log"].with_user(self.manager).search([])
        self.assertIn(
            self.session.log_ids.filtered(
                lambda entry: entry.result == "accepted"), visible)
        self.assertNotIn(foreign, visible)

    def test_09_access_control(self):
        with self.assertRaises(AccessError):
            self.env["scan_pack.session"].with_user(self.outsider).create({
                "picking_id": self.picking.id,
            })
        with self.assertRaises(AccessError):
            self.env["scan_pack.session"].with_user(
                self.outsider).search([])
        self.session.with_user(self.manager).read()
        self.session.with_user(self.manager).write({"note": "Manager note"})
