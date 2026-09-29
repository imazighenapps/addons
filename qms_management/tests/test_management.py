"""Test smoke : la suite QMS Management est installee et coherente."""
from odoo.tests.common import TransactionCase


class TestQmsManagementSuite(TransactionCase):
    def test_suite_modules_installed(self):
        expected = [
            'qms_core', 'qms_documents', 'qms_audit', 'qms_ncr_capa',
            'qms_training', 'qms_objectives', 'qms_management_review',
            'qms_dashboard', 'qms_supplier', 'qms_certification',
            'qms_context', 'qms_complaints', 'qms_measurement',
            'qms_improvement',
        ]
        installed = self.env['ir.module.module'].search([
            ('name', 'in', expected), ('state', '=', 'installed'),
        ]).mapped('name')
        for name in expected:
            self.assertIn(name, installed, 'module %s non installe' % name)

    def test_core_models_available(self):
        for model in ('qms.standard', 'qms.requirement', 'qms.process',
                      'qms.risk', 'qms.control', 'qms.evidence'):
            self.assertIn(model, self.env, 'modele %s manquant' % model)
