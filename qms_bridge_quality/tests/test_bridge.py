from odoo.tests.common import TransactionCase

class TestQmsQualityBridge(TransactionCase):
    def test_quality_check_bridge_field_exists(self):
        self.assertTrue(self.env["quality.check"]._fields.get("qms_ncr_id"))

