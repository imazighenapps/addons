from odoo.tests.common import TransactionCase

from ..services.risk_service import assess


class TestGuardianRisk(TransactionCase):
    def test_security_is_critical(self):
        result = assess({'category': 'security', 'model': 'res.users'}, 'modified')
        self.assertEqual(result['level'], 'critical')

    def test_automation_is_high(self):
        result = assess({'category': 'automation', 'model': 'ir.cron'}, 'modified')
        self.assertEqual(result['level'], 'high')

