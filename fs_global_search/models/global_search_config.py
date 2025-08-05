from odoo import models, fields,api,_
import re
import datetime





class globalSearchConfig(models.TransientModel):


    _name = 'global.search.config'
    _description= 'Global Search Config'


    name        = fields.Char(string='Keyword to Search', required=True)
    model_ids   = fields.Many2many('ir.model', string='Models to Search In', required=True,ondelete='cascade',
                                  domain="[('access_ids','!=',False),('transient','=',False),('model','not ilike','base_import%'),('model','not ilike','ir.%'),('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),('model','!=','mail.thread'),('model','not ilike','dash%')]"
                        )
    line_ids    = fields.One2many('global.search.config.line', 'config_id', string='Line')
    result      = fields.Integer('Results Count',compute="_compute_result")


  


    @api.depends('line_ids')
    def _compute_result(self):
        for rec in self:
            rec.result = len(rec.line_ids)






    @api.onchange("model_ids","name")
    def _onchange_model_ids(self):
        self.line_ids = False
        if self.name and self.model_ids:
            results = []
            for model in self.model_ids:
                Model = self.env[model.model]
               
                fields = [f for f in Model._fields if Model._fields[f].type in ['char', 'text'] and Model._fields[f].store]
                fields +=[f"{fname}.name" for fname, field in Model._fields.items() if field.type == 'many2one' and field.store and hasattr(field, 'comodel_name') and 'name' in self.env[field.comodel_name]._fields]
                domain = ['|'] * (len(fields)-1)
                if not fields:
                    continue
                for field in fields:
                    domain.append((field, 'ilike', self.name))
             
                records = Model.search(domain)
                for rec in records:
                    results.append({
                        'id': rec.id,
                        'technical_model_name': model.model,
                        'display_name': rec.display_name,
                        'model_name':model.display_name,
                    })
            lines = []
            for res in results:
                lines.append((0,0,{
                        "model_id":res['id'],
                        "model_name":res["model_name"],          
                        "display_name":res["display_name"] ,
                        "technical_model_name":res["technical_model_name"] ,
                }))

            self.line_ids = lines



