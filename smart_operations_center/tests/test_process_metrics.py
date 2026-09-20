from odoo.tests.common import TransactionCase


class TestProcessMetrics(TransactionCase):
    def test_percentiles(self):
        analyzer = self.env['smart.operations.process.analyzer']
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(analyzer._percentile(values, 0.50), 3.0)
        self.assertEqual(analyzer._percentile(values, 0.90), 4.6)

    def test_risk_explanation_factors_are_bounded(self):
        score, factors = self.env['smart.operations.risk.engine'].calculate(
            delay_days=20,
            deadline_days=10,
            impact=500000,
            dependency_count=10,
            customer_count=20,
            rule_weight=10,
        )
        self.assertEqual(score, 100.0)
        self.assertLessEqual(factors['delay'], 30.0)
        self.assertLessEqual(factors['deadline'], 15.0)
        self.assertLessEqual(factors['business_impact'], 25.0)
