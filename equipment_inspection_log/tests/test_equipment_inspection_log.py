# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEquipmentInspectionLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["maintenance.equipment"].create({"name": "Eq A"})
        cls.inspector = cls.env["hr.employee"].create({"name": "Inspector A"})
        cls.manager = cls._user(
            "einsp-manager", ["equipment_inspection_log.group_equipmentins_user"])
        cls.outsider = cls._user("einsp-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _rec(self):
        return self.env["equipment.inspection.log"].create({
            "equipment_id": self.equipment.id,
            "inspector_id": self.inspector.id,
            "company_id": self.env.company.id,
        })

    def test_01_done_close(self):
        r = self._rec()
        r.action_done()
        self.assertEqual(r.state, "done")
        r.action_close()
        self.assertEqual(r.state, "closed")

    def test_02_issue_flow(self):
        r = self._rec()
        r.action_issue()
        self.assertEqual(r.state, "issue_found")
        r.action_close()
        self.assertEqual(r.state, "closed")

    def test_03_state_guards(self):
        r = self._rec()
        with self.assertRaises(UserError):
            r.action_close()
        r.action_done()
        with self.assertRaises(UserError):
            r.action_done()

    def test_04_access_control(self):
        r = self._rec()
        with self.assertRaises(Exception):
            self.env["equipment.inspection.log"].with_user(self.outsider).create({
                "equipment_id": self.equipment.id,
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "EI B"})
        foreign = self.env["equipment.inspection.log"].create({
            "equipment_id": self.equipment.id,
            "company_id": company_b.id,
        })
        visible = self.env["equipment.inspection.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
