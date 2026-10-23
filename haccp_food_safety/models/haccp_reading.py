# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HaccpReading(models.Model):
    _name = "haccp.reading"
    _description = "HACCP Monitoring Reading"
    _order = "date desc"

    ccp_id = fields.Many2one("haccp.ccp", string="CCP", required=True,
                             ondelete="restrict")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    value = fields.Float(required=True)
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    equipment_ref = fields.Char(string="Equipment")
    lot_id = fields.Many2one("stock.lot", string="Lot")
    picking_id = fields.Many2one("stock.picking", string="Transfer")
    result = fields.Selection(
        [("ok", "Within Limits"), ("ko", "Out of Limits")],
        compute="_compute_result", store=True,
    )
    note = fields.Text()
    nc_id = fields.Many2one("haccp.nonconformity", string="Non-Conformity", copy=False)

    @api.depends("value", "ccp_id.limit_min", "ccp_id.limit_max")
    def _compute_result(self):
        for rec in self:
            ccp = rec.ccp_id
            if ccp.limit_min and rec.value < ccp.limit_min:
                rec.result = "ko"
            elif ccp.limit_max and rec.value > ccp.limit_max:
                rec.result = "ko"
            else:
                rec.result = "ok"

    def action_create_nc(self):
        for rec in self:
            if rec.nc_id:
                continue
            nc = self.env["haccp.nonconformity"].create({
                "name": _("Out of limits: %s = %s") % (rec.ccp_id.name, rec.value),
                "ccp_id": rec.ccp_id.id,
                "reading_id": rec.id,
                "severity": "major",
                "immediate_action": _("Blocked lot, check the batch."),
            })
            rec.nc_id = nc.id
