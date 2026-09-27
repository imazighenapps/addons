from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError


class TestMrpReadiness(TransactionCase):

    def test_config_defaults_to_block(self):
        rec = self.env['fs.mrp.readiness.config'].create({'company_id': self.env.company.id})
        self.assertTrue(rec.check_workcenters)
        self.assertEqual(rec.blocking_policy, 'block')

    def test_operation_category_is_supported(self):
        categories = dict(self.env['fs.mrp.readiness.item']._fields['category'].selection)
        self.assertIn('operation', categories)

    def test_check_model_can_be_created_only_once_for_an_mo(self):
        template = self.env['product.template'].create({'name': 'Readiness Test Product', 'is_storable': True})
        product = template.product_variant_id
        mo = self.env['mrp.production'].create({
            'product_id': product.id,
            'product_qty': 1.0,
            'product_uom_id': product.uom_id.id,
        })
        action = mo.action_fs_check_readiness()
        check = self.env['fs.mrp.readiness.check'].browse(action['res_id'])
        self.assertEqual(check.production_id, mo)
        with self.assertRaises(UserError):
            self.env['fs.mrp.readiness.check'].create({'production_id': mo.id})
