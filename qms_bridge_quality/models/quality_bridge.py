from odoo import fields, models, _
from odoo.exceptions import UserError

class QualityCheckQms(models.Model):
    _inherit = "quality.check"
    qms_ncr_id = fields.Many2one("qms.ncr", string="QMS NCR", readonly=True, copy=False)

    def action_qms_create_ncr(self):
        self.ensure_one()
        if self.quality_state != "fail":
            raise UserError(_("A QMS NCR can only be created from a failed quality check."))
        if self.qms_ncr_id:
            return {"type":"ir.actions.act_window","res_model":"qms.ncr","res_id":self.qms_ncr_id.id,"view_mode":"form"}
        label = self.point_id.display_name if self.point_id else _("Quality Check Failure")
        ncr = self.env["qms.ncr"].create({
            "name": _("Quality Check Failure: %s") % label,
            "company_id": self.env.company.id,
            "source": "inspection",
            "severity": "major",
            "description": self.note or label or _("Failed quality check"),
        })
        self.qms_ncr_id = ncr.id
        return {"type":"ir.actions.act_window","res_model":"qms.ncr","res_id":ncr.id,"view_mode":"form"}
