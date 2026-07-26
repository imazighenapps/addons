from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    min_margin_percent = fields.Float(
        string="Default Minimum Margin (%)",
        config_parameter="sale_margin_block_pro.min_margin_percent",
        help="Applied when no margin rule (product, category or "
             "customer) matches the order.",
    )
