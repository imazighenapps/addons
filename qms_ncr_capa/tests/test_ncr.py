from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestQmsNcr(TransactionCase):
    def test_ncr_requires_root_cause_before_action_plan(self):
        ncr = self.env["qms.ncr"].create({"name": "Process deviation", "description": "A required record was missing."})
        ncr.action_start_containment(); ncr.containment = "Immediate correction completed."
        ncr.action_start_analysis()
        with self.assertRaises(UserError):
            ncr.action_open_action_plan()

    def test_ncr_cannot_close_without_effective_capa(self):
        ncr = self.env["qms.ncr"].create({"name": "Process deviation", "description": "A required record was missing."})
        ncr.root_cause = "Insufficient verification."
        ncr.containment = "Immediate correction completed."
        ncr.action_start_containment(); ncr.action_start_analysis(); ncr.action_open_action_plan()
        self.env["qms.capa"].create({"ncr_id": ncr.id, "name": "Add verification", "action_description": "Add a second-level verification step."})
        with self.assertRaises(UserError):
            ncr.action_close()
