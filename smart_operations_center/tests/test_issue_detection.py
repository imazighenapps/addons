from odoo.tests.common import TransactionCase


class TestIssueDetection(TransactionCase):
    def test_create_issue_from_rule(self):
        model = self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1)
        rule = self.env['smart.operations.rule'].create({
            'name': 'Test Partner Rule', 'model_id': model.id, 'domain': "[('active', '=', True)]",
            'rule_issue_type': 'missing_action', 'severity': 'medium', 'action_create_activity': False,
        })
        partner = self.env['res.partner'].create({'name': 'Operations Test Partner'})
        self.env['smart.operations.issue.detector'].run_rules()
        issue = self.env['smart.operations.issue'].search([('rule_id', '=', rule.id), ('root_res_id', '=', partner.id)], limit=1)
        self.assertTrue(issue)
