from odoo import fields, models, _

class SaleOrderQms(models.Model):
    _inherit = "sale.order"
    qms_ncr_ids = fields.One2many("qms.ncr", "sale_order_id", string="QMS NCRs")
    qms_ncr_count = fields.Integer(compute="_compute_qms_ncr_count")

    def _compute_qms_ncr_count(self):
        for rec in self:
            rec.qms_ncr_count = len(rec.qms_ncr_ids)

    def action_open_qms_ncrs(self):
        self.ensure_one()
        return {"type":"ir.actions.act_window","name":_("QMS NCR"),"res_model":"qms.ncr","view_mode":"list,form","domain":[("sale_order_id","=",self.id)]}

    def action_create_qms_ncr(self):
        self.ensure_one()
        ncr=self.env["qms.ncr"].create({"name": _("Sales Order Quality Issue: %s") % self.name, "company_id": self.company_id.id, "source":"process", "severity":"minor", "sale_order_id":self.id, "description": _("Quality issue raised from Sales Order %s.") % self.name})
        return {"type":"ir.actions.act_window","name":_("QMS NCR"),"res_model":"qms.ncr","res_id":ncr.id,"view_mode":"form"}

class PurchaseOrderQms(models.Model):
    _inherit = "purchase.order"
    qms_ncr_ids = fields.One2many("qms.ncr", "purchase_order_id", string="QMS NCRs")
    qms_ncr_count = fields.Integer(compute="_compute_qms_ncr_count")

    def _compute_qms_ncr_count(self):
        for rec in self:
            rec.qms_ncr_count = len(rec.qms_ncr_ids)

    def action_open_qms_ncrs(self):
        self.ensure_one()
        return {"type":"ir.actions.act_window","name":_("QMS NCR"),"res_model":"qms.ncr","view_mode":"list,form","domain":[("purchase_order_id","=",self.id)]}

    def action_create_qms_ncr(self):
        self.ensure_one()
        ncr=self.env["qms.ncr"].create({"name": _("Purchase Order Quality Issue: %s") % self.name, "company_id": self.company_id.id, "source":"supplier", "severity":"minor", "purchase_order_id":self.id, "description": _("Quality issue raised from Purchase Order %s.") % self.name})
        return {"type":"ir.actions.act_window","name":_("QMS NCR"),"res_model":"qms.ncr","res_id":ncr.id,"view_mode":"form"}

class QmsNcrSalePurchaseBridge(models.Model):
    _inherit = "qms.ncr"
    sale_order_id = fields.Many2one("sale.order", string="Sales Order", ondelete="set null", check_company=True)
    purchase_order_id = fields.Many2one("purchase.order", string="Purchase Order", ondelete="set null", check_company=True)
