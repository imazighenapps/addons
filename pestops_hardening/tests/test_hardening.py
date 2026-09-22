from odoo.tests.common import TransactionCase


class TestPestOpsHardening(TransactionCase):
    def test_settings_singleton(self):
        settings_model = self.env["pestops.production.settings"]
        first = settings_model.get_for_company(self.env.company)
        second = settings_model.get_for_company(self.env.company)
        self.assertEqual(first.id, second.id)
