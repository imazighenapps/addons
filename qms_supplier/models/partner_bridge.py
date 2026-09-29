from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    qms_supplier_profile_count = fields.Integer(compute="_compute_qms_supplier_counts")
    qms_supplier_evaluation_count = fields.Integer(compute="_compute_qms_supplier_counts")
    qms_supplier_certificate_count = fields.Integer(compute="_compute_qms_supplier_counts")

    def _compute_qms_supplier_counts(self):
        Supplier = self.env["qms.supplier"]
        for partner in self:
            profiles = Supplier.search([("partner_id", "=", partner.id), ("company_id", "=", self.env.company.id)])
            partner.qms_supplier_profile_count = len(profiles)
            partner.qms_supplier_evaluation_count = sum(len(p.evaluation_ids) for p in profiles)
            partner.qms_supplier_certificate_count = sum(len(p.certificate_ids) for p in profiles)

    def action_open_qms_supplier_profile(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", "name": "QMS Supplier Profile",
            "res_model": "qms.supplier", "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id), ("company_id", "=", self.env.company.id)],
        }
