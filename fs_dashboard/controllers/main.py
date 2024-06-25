# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import  request
import logging
_logger = logging.getLogger(__name__)



class Main(http.Controller):



    @http.route('/get/data', auth='user', type='json')
    def get_query_result(self, **kw):
        dashboard_obj = request.env['dashboard.config'].sudo().search([('id', '=', kw.get('dashboard_id'))])
        data = {
            'tiles': self.get_tiles_data(dashboard_obj),
            'sharts': self.get_shart_data(dashboard_obj),
        }
        return data


    def get_tiles_data(self, dashboard_obj):
        data = []
        for item in dashboard_obj.items_ids:
            if item.item_type == 'tile':
                domain  =   eval(item.domain) if item.domain else []
                value = 0
                records = request.env[item.model_id.model].sudo().search(domain)
                count_field = item.count_field.name

                if item.count_type == 'count':
                    value = self.format_value(len(records))
                elif item.count_type == 'sum':
                    value = self.format_value(sum(r[count_field] for r in records))
                elif item.count_type == 'average':
                    value = self.format_value(sum(r[count_field] for r in records) / len(records)) if records else 0

                background_color = ""
                if item.tile_color_from and item.tile_color_to:
                    background_color = "background: linear-gradient(to right, {}, {}) !important;".format(item.tile_color_from, item.tile_color_to)
                elif item.tile_color_from:
                    background_color = "background-color: {} !important;".format(item.tile_color_from)
                elif item.tile_color_to:
                    background_color = "background-color: {} !important;".format(item.tile_color_to)

                text_color = "color: {};".format(item.text_color) if item.text_color else ""
                data.append({
                    'id': item.id,
                    'domain':domain,
                    'count_type':item.count_type,
                    'count_field' : item.count_field.name,
                    'model':item.model_id.model,
                    'name': item.name,
                    'value': value,
                    'icon': 'fa '+item.fa_icon if item.fa_icon else '',
                    'tile_color': background_color,
                    'text_color': text_color.replace(';',''),
                    'icon_color': 'color: #1f6abb',
                })
        return data 

    def get_shart_data(self, dashboard_obj):
        data = []
        for item in dashboard_obj.items_ids:
            if item.item_type != 'tile':
                obj = request.env[item.model_id.model].sudo()
                domain  =   eval(item.domain) if item.domain else []
                groupby =  f"{item.group_by_field.name}{':' + item.date_group if item.group_by_field.ttype in ['date','datetime'] else ''}"
                fields  =   [item.measure_id.name]
                result  =   obj.read_group(domain=domain,fields=fields,groupby=groupby,lazy=False)
                labels = []
                sums = []
                domains=[]
                for r in result:
                    domains.append(r.get('__domain'))
                    if item.measure_id.name == 'id':
                        sums.append(r.get('__count'))
                    else:
                        sums.append(r.get(item.measure_id.name))
                    if item.group_by_field.ttype == 'many2one':
                        mdl = item.group_by_field.relation
                        many2one_id = r.get(groupby)[0] if r.get(groupby) else False
                        name = request.env[mdl].sudo().search([('id','=', many2one_id)]).name
                        labels.append(name)
                    else:
                        labels.append(r.get(groupby))
                data.append({
                    'id': item.id,
                    'type': item.item_type,
                    'title': item.name,
                    'domains': domains,
                    'item'   : item,
                    'groupby': groupby,
                    'group_by_field_ttype': item.group_by_field.ttype,
                    'measure' :   item.measure_id.name,
                    'global_domain':domain,
                    'model':item.model_id.model,
                    'data': {
                        'labels': labels,
                        'datasets': [{
                            'label':'',
                            'data': sums  ,
                            'model': item.model_id.model,
                            'borderWidth': 1
                        }]
                    },
                    
                })
        return data



    def format_value(self,value):
        val = value
        magnitude = 0
        while abs(value) >= 1000:
            magnitude += 1
            value /= 1000.0
            val = '%.2f%s' % (value, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
        return val

