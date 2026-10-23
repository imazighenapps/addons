# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_doc_ids = fields.One2many("supplier.document", "partner_id",
                                      string="Supplier Documents")
    supplier_file_score = fields.Integer(
        compute="_compute_supplier_file", string="File Score (%)")
    supplier_file_complete = fields.Boolean(
        compute="_compute_supplier_file")
    supplier_file_blocking = fields.Boolean(
        compute="_compute_supplier_file")
    supplier_block_payments = fields.Boolean(
        string="Block Payments (incomplete file)",
        help="Prevent posting supplier bills while the file is incomplete.")
    supplier_doc_count_missing = fields.Integer(
        compute="_compute_supplier_file")

    def _compute_supplier_file(self):
        rec_model = self.env["supplier.file.status"]
        for partner in self:
            rec = rec_model.evaluate_partner(partner)
            partner.supplier_file_score = rec.score
            partner.supplier_file_complete = rec.complete
            partner.supplier_file_blocking = rec.blocking
            partner.supplier_doc_count_missing = (len(rec.missing_ids)
                                                  + len(rec.expired_ids))

    def action_open_file(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Supplier File",
            "res_model": "supplier.document",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }


class AccountMove(models.Model):
    _inherit = "account.move"

    def _supplier_file_soft_block(self):
        """Draft-side guard, run before posting vendor bills."""
        for move in self.filtered(lambda m: m.move_type == "in_invoice"):
            partner = move.commercial_partner_id
            if not partner.supplier_block_payments:
                continue
            if not partner.supplier_file_blocking:
                continue
            rec = self.env["supplier.file.status"].evaluate_partner(partner)
            raise UserError(
                "Payment blocked: the supplier file is incomplete (%s). "
                "Turn off 'Block Payments' on the supplier if this must go "
                "through." % ", ".join(rec.blocking_ids.mapped("name")))

    def action_post(self):
        self._supplier_file_soft_block()
        return super().action_post()