from odoo import models, fields,api


class globalSearchConfigLine(models.TransientModel):
    _name = 'global.search.config.line'
    _description= 'Global Search Config Line'
    _order = "model_name asc"

    model_id             = fields.Integer(string='Model id', required=True)
    technical_model_name = fields.Char(string='Technical Model Name', required=True)
    model_name           = fields.Char(string='Model Name', required=True)
    display_name         = fields.Char(string='Display Name', required=True)

    config_id            = fields.Many2one('global.search.config',string='Config') 
    
 

    def show_records(self):
        return {
            'name': '',
            'type': 'ir.actions.act_window',
            'views': [(False, 'form')],
            'res_model': self.technical_model_name,
            'res_id': self.model_id,
            'target': 'new',
        }  
    