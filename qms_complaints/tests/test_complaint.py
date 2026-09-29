from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestQmsComplaint(TransactionCase):
    def test_resolution_required(self):
        complaint = self.env['qms.complaint'].create({'name': 'Delivery issue', 'partner_id': self.env.user.partner_id.id, 'description': 'Test'})
        complaint.action_investigate()
        with self.assertRaises(UserError):
            complaint.action_resolve()
        complaint.resolution = 'Corrective response communicated.'
        complaint.action_resolve()
        self.assertEqual(complaint.state, 'resolved')

    def test_sla_requires_positive_durations(self):
        with self.assertRaises(Exception):
            self.env["qms.complaint"].create({"name":"Invalid SLA", "partner_id":self.env.user.partner_id.id, "description":"Test", "response_sla_hours":0})

    def test_complaint_escalation_creates_ncr(self):
        complaint = self.env["qms.complaint"].create({"name":"Escalate me", "partner_id":self.env.user.partner_id.id, "description":"Critical defect", "priority":"3"})
        complaint.action_escalate_to_ncr()
        self.assertTrue(complaint.ncr_id)
        self.assertEqual(complaint.ncr_id.source, "complaint")
