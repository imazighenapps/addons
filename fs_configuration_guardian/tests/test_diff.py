from odoo.tests.common import TransactionCase

from ..services.diff_service import GuardianDiffService


class TestGuardianDiff(TransactionCase):
    def test_added_modified_removed_and_unchanged(self):
        service = GuardianDiffService(self.env)
        before = self.env['fs.guardian.snapshot'].create({'name': 'Before', 'company_id': self.env.company.id, 'payload': {'items': [
            {'category': 'security', 'model': 'x.model', 'key': '1', 'checksum': 'a', 'data': {'value': 1}},
            {'category': 'technical', 'model': 'x.model', 'key': '2', 'checksum': 'same', 'data': {'value': 2}},
            {'category': 'technical', 'model': 'x.model', 'key': '3', 'checksum': 'old', 'data': {'value': 3}},
        ]}})
        after = self.env['fs.guardian.snapshot'].create({'name': 'After', 'company_id': self.env.company.id, 'payload': {'items': [
            {'category': 'security', 'model': 'x.model', 'key': '1', 'checksum': 'b', 'data': {'value': 9}},
            {'category': 'technical', 'model': 'x.model', 'key': '2', 'checksum': 'same', 'data': {'value': 2}},
            {'category': 'technical', 'model': 'x.model', 'key': '4', 'checksum': 'new', 'data': {'value': 4}},
        ]}})
        changes = service.compare(before, after)
        self.assertEqual({c['operation'] for c in changes}, {'modified', 'removed', 'added'})

