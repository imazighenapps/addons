from odoo import api, fields, models


class QmsRequirementDashboardBridge(models.Model):
    _inherit = "qms.requirement"

    valid_evidence_count = fields.Integer(compute="_compute_dashboard_stats", string="Valid Evidence")
    open_ncr_count = fields.Integer(compute="_compute_dashboard_stats", string="Open NCR")
    open_capa_count = fields.Integer(compute="_compute_dashboard_stats", string="Open CAPA")
    support_score = fields.Float(compute="_compute_dashboard_stats", string="Support %", digits=(16, 2))

    @api.depends("evidence_ids", "evidence_ids.status", "compliance_state")
    def _compute_dashboard_stats(self):
        for requirement in self:
            valid = requirement.evidence_ids.filtered(lambda evidence: evidence.status == "valid")
            ncrs = self.env["qms.ncr"].search_count([
                ("company_id", "=", requirement.company_id.id),
                ("requirement_id", "=", requirement.id),
                ("status", "!=", "closed"),
            ])
            capas = self.env["qms.capa"].search_count([
                ("company_id", "=", requirement.company_id.id),
                ("ncr_id.requirement_id", "=", requirement.id),
                ("status", "not in", ["effective", "cancelled"]),
            ])
            requirement.valid_evidence_count = len(valid)
            requirement.open_ncr_count = ncrs
            requirement.open_capa_count = capas
            requirement.support_score = 100.0 if requirement.compliance_state == "supported" else 50.0 if requirement.compliance_state == "partial" else 0.0
