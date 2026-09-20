from odoo.tests.common import TransactionCase

class TestShiftFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env['shiftflow.team'].create({'name': 'Test Team', 'code': 'TEST'})
        cls.s1 = cls.env['shiftflow.shift'].create({'date':'2026-09-18','start_datetime':'2026-09-18 06:00:00','end_datetime':'2026-09-18 14:00:00','team_id':cls.team.id})
        cls.s2 = cls.env['shiftflow.shift'].create({'date':'2026-09-18','start_datetime':'2026-09-18 14:00:00','end_datetime':'2026-09-18 22:00:00','team_id':cls.team.id})
    def test_adjacent_shifts(self):
        self.assertEqual(self.s1.next_shift_id, self.s2)
        self.assertEqual(self.s2.previous_shift_id, self.s1)
    def test_handover(self):
        self.env['shiftflow.incident'].create({'name':'Incident','shift_id':self.s1.id,'description':'Test','severity':'high','carry_over':True})
        self.env['shiftflow.task'].create({'name':'Task','shift_id':self.s1.id,'deadline':'2026-09-18 15:00:00','carry_over':True})
        self.s1.state='closing'
        ho=self.env['shiftflow.handover'].create({'outgoing_shift_id':self.s1.id,'incoming_shift_id':self.s2.id})
        self.assertEqual(len(ho.item_ids),2)
        ho.action_prepare(); ho.action_send(); ho.action_accept()
        self.assertTrue(self.s2.incident_ids.filtered(lambda x: x.carried_from_id))
        self.assertTrue(self.s2.task_ids.filtered(lambda x: x.carried_from_id))
