from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    min_margin_percent = fields.Float(
        string="Minimum Margin (%)",
        config_parameter="sale_margin_block.min_margin_percent",
        digits=(16, 2),
    )
