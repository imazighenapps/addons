from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError


class TestBackorderControl(TransactionCase):

    def test_configuration_thresholds(self):
        config = self.env['fs.backorder.control.config'].create({'company_id': self.env.company.id})
        self.assertEqual(config.aging_days, 7)
        self.assertEqual(config.critical_days, 30)

    def test_invalid_thresholds_are_rejected(self):
        with self.assertRaises(IntegrityError):
            self.env['fs.backorder.control.config'].create({
                'company_id': self.env.company.id,
                'aging_days': 31,
                'critical_days': 30,
            })

    def test_duplicate_configuration_is_rejected(self):
        self.env['fs.backorder.control.config'].create({'company_id': self.env.company.id})
        with self.assertRaises(IntegrityError):
            self.env['fs.backorder.control.config'].create({'company_id': self.env.company.id})

    def test_empty_refresh_is_safe(self):
        self.env['fs.backorder.control'].cron_refresh(batch_size=50)
