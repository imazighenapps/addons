# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sdd_mandate_ids = fields.One2many("sdd.mandate", "partner_id", string="SEPA Mandates")
    sdd_mandate_count = fields.Integer(string="SEPA Mandate Count", compute="_compute_sdd_mandate_count")

    def _compute_sdd_mandate_count(self):
        data = self.env["sdd.mandate"]._read_group(
            [("partner_id", "in", self.ids)],
            ["partner_id"],
            ["__count"],
        )
        mapped = {partner.id: count for partner, count in data}
        for partner in self:
            partner.sdd_mandate_count = mapped.get(partner.id, 0)

    def action_view_sdd_mandates(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sepa_direct_debit.action_sdd_mandate")
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {
            "default_partner_id": self.id,
            "default_company_id": self.env.company.id,
        }
        return action
