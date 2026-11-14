# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestServiceChecklist(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env["service.checklist.template"].create({
            "name": "Visit Checklist",
            "company_id": cls.env.company.id,
            "item_ids": [
                (0, 0, {"name": "Step 1", "sequence": 1}),
                (0, 0, {"name": "Step 2", "sequence": 2}),
            ],
        })
        cls.manager = cls._user(
            "checklist-manager", ["service_checklist.group_servicecheck_user"])
        cls.outsider = cls._user(
            "checklist-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def test_01_create_run_and_complete(self):
        action = self.template.action_create_run()
        run = self.env["service.checklist.run"].browse(action["res_id"])
        self.assertEqual(len(run.line_ids), 2)
        self.assertEqual(run.state, "draft")
        self.assertAlmostEqual(run.progress, 0.0)
        with self.assertRaises(UserError):
            run.action_complete()
        run.line_ids.write({"result": "done"})
        self.assertAlmostEqual(run.progress, 100.0)
        run.action_complete()
        self.assertEqual(run.state, "done")
        self.assertTrue(run.date_done)

    def test_02_partial_progress(self):
        action = self.template.action_create_run()
        run = self.env["service.checklist.run"].browse(action["res_id"])
        run.line_ids[0].result = "done"
        self.assertAlmostEqual(run.progress, 50.0)
        self.assertEqual(run.state, "draft")

    def test_03_cannot_cancel_completed(self):
        action = self.template.action_create_run()
        run = self.env["service.checklist.run"].browse(action["res_id"])
        run.line_ids.write({"result": "done"})
        run.action_complete()
        with self.assertRaises(UserError):
            run.action_cancel()

    def test_04_access_control(self):
        action = self.template.action_create_run()
        run = self.env["service.checklist.run"].browse(action["res_id"])
        with self.assertRaises(Exception):
            self.env["service.checklist.run"].with_user(self.outsider).create({
                "name": "No access",
                "company_id": self.env.company.id,
            })
        run.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Check B"})
        foreign = self.env["service.checklist.template"].create({
            "name": "Foreign Template",
            "company_id": company_b.id,
            "item_ids": [(0, 0, {"name": "Step", "sequence": 1})],
        })
        visible = self.env["service.checklist.template"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
