from odoo import fields, models, _

class StockPickingQms(models.Model):
    _inherit = "stock.picking"
    qms_ncr_ids = fields.One2many("qms.ncr", "stock_picking_id", string="QMS NCRs")
    qms_ncr_count = fields.Integer(compute="_compute_qms_ncr_count")
    def _compute_qms_ncr_count(self):
        for rec in self: rec.qms_ncr_count = len(rec.qms_ncr_ids)
    def action_open_qms_ncrs(self):
        self.ensure_one(); return {"type":"ir.actions.act_window","name":_("QMS NCR"),"res_model":"qms.ncr","view_mode":"list,form","domain":[("stock_picking_id","=",self.id)]}
    def action_create_qms_ncr(self):
        self.ensure_one(); ncr=self.env["qms.ncr"].create({"name": _("Transfer Quality Issue: %s") % self.name, "company_id": self.company_id.id, "source":"inspection", "severity":"minor", "stock_picking_id":self.id, "description": _("Quality issue raised from transfer %s.") % self.name}); return {"type":"ir.actions.act_window","name":_("QMS NCR"),"res_model":"qms.ncr","res_id":ncr.id,"view_mode":"form"}

class MrpProductionQms(models.Model):
    _inherit = "mrp.production"
    qms_ncr_ids = fields.One2many("qms.ncr", "mrp_production_id", string="QMS NCRs")
    qms_ncr_count = fields.Integer(compute="_compute_qms_ncr_count")
    def _compute_qms_ncr_count(self):
        for rec in self: rec.qms_ncr_count = len(rec.qms_ncr_ids)
    def action_open_qms_ncrs(self):
        self.ensure_one(); return {"type":"ir.actions.act_window","name":_("QMS NCR"),"res_model":"qms.ncr","view_mode":"list,form","domain":[("mrp_production_id","=",self.id)]}
    def action_create_qms_ncr(self):
        self.ensure_one(); ncr=self.env["qms.ncr"].create({"name": _("Manufacturing Quality Issue: %s") % self.name, "company_id": self.company_id.id, "source":"inspection", "severity":"minor", "mrp_production_id":self.id, "description": _("Quality issue raised from Manufacturing Order %s.") % self.name}); return {"type":"ir.actions.act_window","name":_("QMS NCR"),"res_model":"qms.ncr","res_id":ncr.id,"view_mode":"form"}

class QmsNcrStockMrpBridge(models.Model):
    _inherit = "qms.ncr"
    stock_picking_id = fields.Many2one("stock.picking", string="Transfer", ondelete="set null", check_company=True)
    mrp_production_id = fields.Many2one("mrp.production", string="Manufacturing Order", ondelete="set null", check_company=True)
