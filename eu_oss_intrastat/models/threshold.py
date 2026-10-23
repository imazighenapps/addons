# -*- coding: utf-8 -*-
from odoo import fields, models

OSS_LIMIT = 10000.0
IOSS_LIMIT = 150.0


class OssThreshold(models.Model):
    _name = "oss.threshold"
    _description = "EU Scheme Threshold"
    _order = "country_id"

    name = fields.Char(required=True)
    scheme = fields.Selection(
        [("oss", "OSS (goods)"), ("ioss", "IOSS (distance sales)")],
        required=True, default="oss")
    limit = fields.Float(string="Threshold (EUR)", default=OSS_LIMIT)
    country_ids = fields.Many2many("res.country", string="EU Countries")
    warn_ratio = fields.Float(string="Warn At (%)", default=0.8)
    active = fields.Boolean(default=True)

    def _limit_for(self, scheme):
        self.ensure_one()
        return self.limit if self.scheme == scheme else 0.0