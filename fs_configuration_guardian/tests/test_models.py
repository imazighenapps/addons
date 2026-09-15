from odoo.tests.common import TransactionCase


class TestGuardianModels(TransactionCase):
    def test_change_creation_is_idempotent(self):
        baseline = self.env['fs.guardian.baseline'].create({'name': 'Test Baseline', 'company_id': self.env.company.id})
        item = {'category': 'security', 'model': 'res.users', 'key': '1', 'label': 'Test User'}
        Change = self.env['fs.guardian.change']
        first = Change.create_change(baseline, item, {'a': 1}, {'a': 2}, 'modified', {'level': 'critical', 'reason': 'Security configuration changed.'})
        second = Change.create_change(baseline, item, {'a': 1}, {'a': 2}, 'modified', {'level': 'critical', 'reason': 'Security configuration changed.'})
        self.assertEqual(first, second)
        self.assertEqual(Change.search_count([('baseline_id', '=', baseline.id)]), 1)

