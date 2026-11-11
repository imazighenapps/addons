# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLabelForge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({"name": "LabelForge Other Company"})
        cls.template = cls.env["label.template"].create({
            "name": "LabelForge Product Template",
            "code": "LF-PRD",
            "label_type": "product",
            "width_mm": 60,
            "height_mm": 40,
            "content": "Product name and barcode",
        })

    def _job(self, template=None, **vals):
        data = {
            "name": "LJ-TEST-001",
            "template_id": (template or self.template).id,
            "target_name": "LF Test Target",
            "quantity": 10,
            "print_date": "2026-02-20",
        }
        data.update(vals)
        return self.env["label.job"].create(data)

    def test_01_template_defaults(self):
        tpl = self.env["label.template"].create({
            "name": "LabelForge Lot Template",
            "label_type": "lot",
        })
        self.assertTrue(tpl.active)
        self.assertEqual(tpl.company_id, self.env.company)
        self.assertEqual(tpl.job_count, 0)

    def test_02_template_dimension_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["label.template"].create({
                "name": "LabelForge Bad Template",
                "label_type": "location",
                "width_mm": 0,
                "height_mm": 20,
            })

    def test_03_job_defaults(self):
        job = self._job(name="LJ-DEF-2026")
        self.assertEqual(job.state, "draft")
        self.assertEqual(job.label_type, "product")
        self.assertFalse(job.printed_on)

    def test_04_job_workflow_print(self):
        job = self._job(name="LJ-WF-2026", print_date="2026-03-05")
        job.action_print()
        self.assertEqual(job.state, "printed")
        self.assertTrue(job.printed_on)

    def test_05_job_cancel_and_reset(self):
        job = self._job(name="LJ-CAN-2026", print_date="2026-03-06")
        job.action_cancel()
        self.assertEqual(job.state, "cancelled")
        job.action_reset()
        self.assertEqual(job.state, "draft")
        with self.assertRaises(UserError):
            job.action_reset()

    def test_06_invalid_job_transitions(self):
        job = self._job(name="LJ-INV-2026", print_date="2026-04-01")
        job.action_print()
        with self.assertRaises(UserError):
            job.action_cancel()

    def test_07_job_quantity_constraint(self):
        with self.assertRaises(ValidationError):
            self._job(name="LJ-QTY-2026", print_date="2026-05-01", quantity=0)

    def test_08_template_job_counter(self):
        self._job(name="LJ-CNT-A-2026", print_date="2026-06-01")
        self._job(name="LJ-CNT-B-2026", print_date="2026-06-02")
        self.template.invalidate_recordset()
        self.assertEqual(self.template.job_count, 2)

    def test_09_multi_company_isolation(self):
        own_tpl = self.template
        foreign_tpl = self.env["label.template"].with_company(self.other_company).create({
            "name": "LabelForge Foreign Template",
            "label_type": "location",
            "width_mm": 80,
            "height_mm": 50,
            "company_id": self.other_company.id,
        })
        foreign_job = self.env["label.job"].with_company(self.other_company).create({
            "name": "LJ-MC-OTH-2026",
            "template_id": foreign_tpl.id,
            "target_name": "Foreign Bin",
            "quantity": 3,
            "print_date": "2026-07-01",
            "company_id": self.other_company.id,
        })
        self.assertEqual(own_tpl.company_id, self.env.company)
        self.assertEqual(foreign_tpl.company_id, self.other_company)
        self.assertNotEqual(own_tpl.company_id, foreign_job.company_id)
        self.assertEqual(foreign_job.state, "draft")
