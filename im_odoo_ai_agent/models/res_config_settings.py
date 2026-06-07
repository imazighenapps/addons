
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_model_name = fields.Char(
        string='GPT4All Model',
        config_parameter='im_odoo_ai_agent.model_name',
    )
    ai_model_path = fields.Char(
        string='Models Path',
        config_parameter='im_odoo_ai_agent.model_path',
    )
    ai_language = fields.Selection([
        ('fr', 'Français'),
        ('en', 'English'),
        ('ar', 'العربية'),
    ], string='Langue IA', config_parameter='im_odoo_ai_agent.language')

    ai_max_tokens = fields.Integer(
        string='Max Tokens',
        config_parameter='im_odoo_ai_agent.max_tokens',
    )
    ai_temperature = fields.Float(
        string='Température',
        config_parameter='im_odoo_ai_agent.temperature',
    )

    def set_values(self):
        super().set_values()
        config = self.env['ai.agent.config'].get_active_config()
        vals = {}
        if self.ai_model_name:
            vals['model_name'] = self.ai_model_name
        if self.ai_model_path:
            vals['model_path'] = self.ai_model_path
        if self.ai_language:
            vals['language'] = self.ai_language
        if self.ai_max_tokens:
            vals['max_tokens'] = self.ai_max_tokens
        if self.ai_temperature:
            vals['temperature'] = self.ai_temperature
        if vals:
            config.write(vals)

    @api.model
    def get_values(self):
        res = super().get_values()
        config = self.env['ai.agent.config'].get_active_config()
        if config:
            res.update({
                'ai_model_name':  config.model_name  or res.get('ai_model_name'),
                'ai_model_path':  config.model_path  or res.get('ai_model_path'),
                'ai_language':    config.language     or res.get('ai_language', 'fr'),
                'ai_max_tokens':  config.max_tokens   or res.get('ai_max_tokens', 1024),
                'ai_temperature': config.temperature  or res.get('ai_temperature', 0.7),
            })
        return res
