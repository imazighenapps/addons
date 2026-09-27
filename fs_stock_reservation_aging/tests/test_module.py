from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError


class TestReservationAging(TransactionCase):

    def test_threshold_defaults(self):
        config = self.env['fs.stock.reservation.aging.config'].create({'company_id': self.env.company.id})
        self.assertEqual(config.aging_days, 7)
        self.assertEqual(config.critical_days, 30)

    def test_invalid_thresholds_are_rejected(self):
        with self.assertRaises(IntegrityError):
            self.env['fs.stock.reservation.aging.config'].create({
                'company_id': self.env.company.id,
                'aging_days': 30,
                'critical_days': 7,
            })

    def test_age_bucket_boundaries_are_configurable(self):
        config = self.env['fs.stock.reservation.aging.config'].create({
            'company_id': self.env.company.id,
            'aging_days': 3,
            'critical_days': 10,
        })
        self.assertLess(config.aging_days, config.critical_days)
