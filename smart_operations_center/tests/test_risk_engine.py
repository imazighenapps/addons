from odoo.tests.common import TransactionCase


class TestRiskEngine(TransactionCase):
    def test_risk_score_is_bounded(self):
        score, factors = self.env['smart.operations.risk.engine'].calculate(
            delay_days=20, deadline_days=-2, impact=500000, dependency_count=10, customer_count=20,
        )
        self.assertEqual(score, 100.0)
        self.assertIn('delay', factors)
