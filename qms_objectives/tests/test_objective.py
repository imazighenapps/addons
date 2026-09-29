from odoo.tests.common import TransactionCase


class TestQmsObjective(TransactionCase):
    def test_progress_increase(self):
        objective = self.env["qms.objective"].create({
            "name": "Reduce customer complaints",
            "direction": "decrease",
            "baseline_value": 100,
            "target_value": 20,
            "company_id": self.env.company.id,
        })
        self.env["qms.objective.measurement"].create({"objective_id": objective.id, "value": 60})
        objective.invalidate_recordset()
        self.assertAlmostEqual(objective.current_value, 60)
        self.assertAlmostEqual(objective.progress_percent, 50)

    def test_objective_starts_at_zero_without_measurement(self):
        objective = self.env["qms.objective"].create({"name":"Target","direction":"increase","baseline_value":0,"target_value":100,"company_id":self.env.company.id})
        self.assertEqual(objective.current_value, 0)
        self.assertEqual(objective.progress_percent, 0)
