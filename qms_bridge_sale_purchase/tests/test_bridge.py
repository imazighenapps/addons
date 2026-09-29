from odoo.tests.common import TransactionCase

class TestQmsSalePurchaseBridge(TransactionCase):
    def test_bridge_module_loads_sale_model(self):
        self.assertTrue(self.env["sale.order"]._fields.get("qms_ncr_ids"))

