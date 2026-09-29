from odoo.tests.common import TransactionCase


class TestQmsStockMrpBridge(TransactionCase):
    def test_bridge_model_fields_are_declared(self):
        self.assertTrue(self.env["stock.picking"]._fields.get("qms_ncr_ids"))
        self.assertTrue(self.env["mrp.production"]._fields.get("qms_ncr_ids"))
