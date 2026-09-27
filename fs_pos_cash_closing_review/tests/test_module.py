from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError


class TestPosCashReview(TransactionCase):

    def test_config_defaults(self):
        rec = self.env['fs.pos.cash.review.config'].create({'company_id': self.env.company.id})
        self.assertGreater(rec.critical_amount, rec.warning_amount)
        self.assertTrue(rec.require_approval_before_close)

    def test_invalid_thresholds_are_rejected(self):
        with self.assertRaises(IntegrityError):
            self.env['fs.pos.cash.review.config'].create({
                'company_id': self.env.company.id,
                'warning_amount': 100,
                'critical_amount': 50,
            })

    def test_review_line_difference_severity_policy(self):
        self.assertEqual(
            self.env['fs.pos.cash.review.line']._fields['severity'].selection,
            [('ok', 'OK'), ('warning', 'Warning'), ('critical', 'Critical')],
        )
