# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRecycle(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage = cls.env["crm.stage"].create({
            "name": "Nurturing", "sequence": 1,
        })
        cls.rule = cls.env["lead.recycling.rule"].create({
            "name": "90d Revival", "inactivity_days": 90,
            "include_lost": True, "target_stage_id": cls.stage.id,
            "max_recycles": 2,
        })

    def _old_lead(self, active=False):
        lead = self.env["crm.lead"].create({
            "name": "Old Lead", "type": "opportunity", "active": active,
        })
        old_date = "2020-01-01 00:00:00"
        self.env.cr.execute(
            "UPDATE crm_lead SET write_date=%s, create_date=%s WHERE id=%s",
            (old_date, old_date, lead.id))
        lead.invalidate_recordset()
        return lead

    def test_01_lost_recycled(self):
        lead = self._old_lead(active=False)
        # run OUR rule only: running every active rule would let another
        # rule recycle the same lead and overwrite its stage
        self.rule._run_rules(self.rule)
        self.assertTrue(lead.active)
        self.assertEqual(lead.stage_id, self.stage)
        self.assertEqual(lead.recycled_count, 1)

    def test_02_max_recycles(self):
        lead = self._old_lead(active=False)
        lead.write({"recycled_count": self.rule.max_recycles})
        self.rule._run_rules(self.rule)
        self.assertFalse(lead.active)

    def test_03_reassign(self):
        self.rule.assignee_id = self.env.user
        lead = self._old_lead(active=False)
        self.rule._run_rules(self.rule)
        self.assertEqual(lead.user_id, self.env.user)
