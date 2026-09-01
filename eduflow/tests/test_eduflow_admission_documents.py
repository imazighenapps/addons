# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import EduflowTestCommon


@tagged('post_install', '-at_install')
class TestEduflowAdmissionDocuments(EduflowTestCommon):
    """F3.3 -- required document tracking and (optional) blocking of
    acceptance while documents are missing."""

    def setUp(self):
        super().setUp()
        self.doc_type = self.env['eduflow.document.type'].create({
            'name': 'Birth Certificate', 'required': True,
        })
        self.admission = self.env['eduflow.admission'].create({
            'student_id': self.student_1.id,
            'level_id': self.level.id,
            'year_id': self.year.id,
        })

    def test_document_lines_prefilled_on_create(self):
        self.assertIn(self.doc_type, self.admission.document_line_ids.mapped('document_type_id'))
        self.assertFalse(self.admission.documents_complete)

    def test_documents_complete_when_all_received(self):
        self.admission.document_line_ids.write({'received': True})
        self.assertTrue(self.admission.documents_complete)

    def test_accept_blocked_when_incomplete_and_enforced(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'eduflow.require_complete_documents', 'True')
        with self.assertRaises(UserError):
            self.admission.action_accept()

    def test_accept_allowed_when_not_enforced(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'eduflow.require_complete_documents', 'False')
        self.admission.action_accept()
        self.assertEqual(self.admission.state, 'accepted')
