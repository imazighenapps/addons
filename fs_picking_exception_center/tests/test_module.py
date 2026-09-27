from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPickingException(TransactionCase):

    def test_configuration_defaults(self):
        config = self.env['fs.picking.exception.config'].create({'company_id': self.env.company.id})
        self.assertEqual(config.critical_after_days, 2)
        self.assertEqual(config.notification_mode, 'activity')

    def test_empty_refresh_is_safe(self):
        self.env['fs.picking.exception'].cron_refresh(batch_size=50)

    def test_negative_threshold_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['fs.picking.exception.config'].create({
                'company_id': self.env.company.id,
                'overdue_minutes': -1,
            })
