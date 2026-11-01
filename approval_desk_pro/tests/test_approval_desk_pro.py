# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestApprovalDeskPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = cls.env["res.users"]
        group_desk = cls.env.ref(
            "approval_desk_pro.group_approvaldesk_user")
        cls.requester = users.create({
            "name": "Approval Desk Requester",
            "login": "apprdesk_requester",
            "email": "apprdesk.requester@example.com",
            "group_ids": [(6, 0, [group_desk.id])],
        })
        cls.approver_1 = users.create({
            "name": "Approval Desk Approver One",
            "login": "apprdesk_approver_1",
            "email": "apprdesk.approver1@example.com",
            "group_ids": [(6, 0, [group_desk.id])],
        })
        cls.approver_2 = users.create({
            "name": "Approval Desk Approver Two",
            "login": "apprdesk_approver_2",
            "email": "apprdesk.approver2@example.com",
            "group_ids": [(6, 0, [group_desk.id])],
        })
        cls.approver_3 = users.create({
            "name": "Approval Desk Approver Three",
            "login": "apprdesk_approver_3",
            "email": "apprdesk.approver3@example.com",
            "group_ids": [(6, 0, [group_desk.id])],
        })
        cls.outsider = users.create({
            "name": "Approval Desk Outsider",
            "login": "apprdesk_outsider",
            "email": "apprdesk.outsider@example.com",
            "group_ids": [(6, 0, [group_desk.id])],
        })

    def _chain(self):
        return [
            (self.approver_1, 0.0),
            (self.approver_2, 5000.0),
            (self.approver_3, 20000.0),
        ]

    def _request(self, amount, steps=None):
        request = self.env["approval.desk.request"].create({
            "model_name": "res.partner",
            "res_id": self.requester.partner_id.id,
            "res_name": "Approval Desk Test Document",
            "amount": amount,
            "requester_id": self.requester.id,
        })
        for index, (approver, threshold) in enumerate(steps or [], start=1):
            self.env["approval.desk.step"].create({
                "request_id": request.id,
                "sequence": index * 10,
                "approver_id": approver.id,
                "min_amount": threshold,
            })
        return request

    def _refresh(self, request):
        request.invalidate_recordset()
        request.step_ids.invalidate_recordset()
        return request

    def _approve(self, request, user):
        request.with_user(user).action_approve()
        return self._refresh(request)

    def test_01_submit_builds_the_chain(self):
        request = self._request(12000.0, self._chain())
        self.assertTrue(request.name.startswith("APR/"))
        self.assertEqual(request.state, "draft")
        self.assertEqual(len(request.step_ids), 3)
        self.assertTrue(request.action_submit())
        self.assertEqual(request.state, "waiting")
        self.assertEqual(len(request.step_ids), 2)
        self.assertEqual(request.step_ids.mapped("approver_id").ids,
                         [self.approver_1.id, self.approver_2.id])
        self.assertEqual(request.step_ids.mapped("sequence"), [10, 20])
        self.assertEqual(request.current_step, request.step_ids[0])
        self.assertEqual(request.current_step.approver_id, self.approver_1)

    def test_02_approve_step_by_step(self):
        request = self._request(12000.0, self._chain())
        request.action_submit()
        first = request.current_step
        self._approve(request, self.approver_1)
        self.assertEqual(first.state, "approved")
        self.assertTrue(first.decision_date)
        self.assertEqual(request.state, "waiting")
        self.assertEqual(request.current_step.approver_id, self.approver_2)
        self.assertEqual(len(request.step_ids.filtered(
            lambda step: step.state == "pending")), 1)

    def test_03_last_step_approves_the_request(self):
        request = self._request(30000.0, self._chain())
        request.action_submit()
        self.assertEqual(len(request.step_ids), 3)
        self._approve(request, self.approver_1)
        self._approve(request, self.approver_2)
        self.assertEqual(request.state, "waiting")
        self._approve(request, self.approver_3)
        self.assertEqual(request.state, "approved")
        self.assertTrue(all(step.state == "approved"
                            for step in request.step_ids))
        self.assertFalse(request.current_step)

    def test_04_refusal_stops_everything(self):
        request = self._request(30000.0, self._chain())
        request.action_submit()
        request.with_user(self.approver_1).action_refuse()
        self._refresh(request)
        self.assertEqual(request.state, "refused")
        self.assertEqual(request.step_ids[0].state, "refused")
        self.assertTrue(request.step_ids[0].decision_date)
        self.assertEqual(request.step_ids[1].state, "pending")
        with self.assertRaises(UserError):
            request.with_user(self.approver_1).action_approve()
        with self.assertRaises(UserError):
            request.with_user(self.approver_2).action_approve()
        self.assertEqual(request.state, "refused")

    def test_05_wrong_user_cannot_approve(self):
        request = self._request(12000.0, self._chain())
        request.action_submit()
        with self.assertRaises(UserError):
            request.with_user(self.approver_2).action_approve()
        with self.assertRaises(UserError):
            request.with_user(self.outsider).action_approve()
        self._refresh(request)
        self.assertEqual(request.state, "waiting")
        self.assertEqual(request.current_step.state, "pending")
        self._approve(request, self.approver_1)
        self.assertEqual(request.current_step.approver_id, self.approver_2)

    def test_06_thresholds_select_the_steps(self):
        small = self._request(100.0, self._chain())
        small.action_submit()
        self.assertEqual(len(small.step_ids), 1)
        self.assertEqual(small.step_ids.approver_id, self.approver_1)

        exact = self._request(5000.0, self._chain())
        exact.action_submit()
        self.assertEqual(len(exact.step_ids), 2)

        big = self._request(75000.0, self._chain())
        big.action_submit()
        self.assertEqual(len(big.step_ids), 3)
        self.assertEqual(big.current_step.approver_id, self.approver_1)

        blocked = self._request(10.0, [(self.approver_3, 20000.0)])
        with self.assertRaises(UserError):
            blocked.action_submit()
        self.assertEqual(blocked.state, "draft")
        self.assertEqual(len(blocked.step_ids), 1)

    def test_07_reset_clears_the_steps(self):
        request = self._request(12000.0, self._chain())
        request.action_submit()
        self._approve(request, self.approver_1)
        self.assertEqual(len(request.step_ids), 2)
        self.assertTrue(request.action_reset())
        self._refresh(request)
        self.assertEqual(request.state, "draft")
        self.assertFalse(request.step_ids)
        self.assertFalse(request.current_step)
        with self.assertRaises(UserError):
            request.action_reset()
        with self.assertRaises(UserError):
            request.action_submit()

    def test_08_submit_twice_is_refused(self):
        request = self._request(12000.0, self._chain())
        request.action_submit()
        with self.assertRaises(UserError):
            request.action_submit()
        self.assertEqual(request.state, "waiting")
        self.assertEqual(len(request.step_ids), 2)
        empty = self._request(12000.0)
        with self.assertRaises(UserError):
            empty.action_submit()
        self.assertEqual(empty.state, "draft")
