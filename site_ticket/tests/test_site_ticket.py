# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSiteTicket(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "SiteTicket Other Company",
        })
        cls.contractor = cls.env["res.partner"].create({
            "name": "SiteTicket Test Contractor",
        })
        cls.area = cls.env["site.area"].create({
            "name": "SiteTicket Test Building A",
            "code": "ST-A",
            "address": "1 Test Street",
        })
        cls.area_b = cls.env["site.area"].create({
            "name": "SiteTicket Test Building B",
            "code": "ST-B",
        })

    def _ticket(self, area=None, **values):
        defaults = {
            "name": "SiteTicket Test Leak",
            "area_id": (area or self.area).id,
            "owner_id": self.env.user.id,
            "contractor_id": self.contractor.id,
            "priority": "2",
            "requested_on": date(2026, 11, 10),
            "deadline_on": date(2026, 11, 15),
            "cost": 120.0,
        }
        defaults.update(values)
        return self.env["site.ticket"].create(defaults)

    def test_01_ticket_defaults(self):
        ticket = self._ticket()
        self.assertEqual(ticket.state, "new")
        self.assertEqual(ticket.company_id, self.env.company)
        self.assertEqual(ticket.priority, "2")
        self.assertFalse(ticket.started_on)
        self.assertFalse(ticket.resolved_on)

    def test_02_workflow_start_done(self):
        ticket = self._ticket()
        self.assertTrue(ticket.action_start())
        self.assertEqual(ticket.state, "in_progress")
        self.assertTrue(ticket.started_on)
        self.assertTrue(ticket.action_done())
        self.assertEqual(ticket.state, "done")
        self.assertTrue(ticket.resolved_on)

    def test_03_workflow_guards(self):
        ticket = self._ticket()
        with self.assertRaises(UserError):
            ticket.action_done()
        ticket.action_start()
        with self.assertRaises(UserError):
            ticket.action_start()
        ticket.action_done()
        with self.assertRaises(UserError):
            ticket.action_cancel()

    def test_04_cancel_and_reset(self):
        ticket = self._ticket()
        ticket.action_start()
        ticket.action_cancel()
        self.assertEqual(ticket.state, "cancelled")
        with self.assertRaises(UserError):
            ticket.action_cancel()
        ticket.action_reset()
        self.assertEqual(ticket.state, "new")
        self.assertFalse(ticket.started_on)
        self.assertFalse(ticket.resolved_on)

    def test_05_deadline_before_request_is_refused(self):
        with self.assertRaises(ValidationError):
            self._ticket(requested_on=date(2026, 11, 10),
                         deadline_on=date(2026, 11, 5))
        with self.assertRaises(ValidationError):
            self._ticket(requested_on=date(2026, 11, 10),
                         resolved_on=date(2026, 11, 1))

    def test_06_negative_cost_is_refused(self):
        with self.assertRaises(ValidationError):
            self._ticket(cost=-10.0)
        ticket = self._ticket(cost=0.0)
        self.assertEqual(ticket.cost, 0.0)

    def test_07_area_counters(self):
        open_ticket = self._ticket(name="SiteTicket Test Open")
        open_ticket.action_start()
        new_ticket = self._ticket(name="SiteTicket Test New")
        done_ticket = self._ticket(name="SiteTicket Test Done")
        done_ticket.action_start()
        done_ticket.action_done()
        self.area.invalidate_recordset()
        self.assertEqual(self.area.ticket_count, 3)
        self.assertEqual(self.area.open_ticket_count, 2)
        self.assertEqual(new_ticket.state, "new")

    def test_08_company_isolation(self):
        foreign_area = self.env["site.area"].with_company(
            self.other_company).sudo().create({
            "name": "SiteTicket Test Foreign Area",
            "company_id": self.other_company.id,
        })
        foreign = self.env["site.ticket"].with_company(
            self.other_company).sudo().create({
            "name": "SiteTicket Test Foreign Ticket",
            "area_id": foreign_area.id,
            "requested_on": date(2026, 12, 1),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._ticket(name="SiteTicket Test Local")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
