from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestQmsDocument(TransactionCase):
    def test_document_requires_approved_version_before_publish(self):
        doc = self.env["qms.document"].create({"name": "Controlled Procedure"})
        doc.action_create_version()
        with self.assertRaises(UserError):
            doc.action_publish()

    def test_document_revision_can_be_created(self):
        doc = self.env["qms.document"].create({"name": "Controlled Procedure"})
        doc.action_create_version()
        self.assertEqual(doc.current_version_id.revision, "1")
        doc.action_create_version()
        self.assertEqual(doc.current_version_id.revision, "2")

    def test_document_version_is_numbered(self):
        doc = self.env["qms.document"].create({"name":"Controlled SOP 2"})
        doc.action_create_version()
        self.assertTrue(doc.current_version_id.revision)
