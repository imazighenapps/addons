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
                value = 0
                records = request.env[item.model_id.model].sudo().search(eval(item.domain) if item.domain else [])
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
                    'name': item.name,
                    'value': value,
                    'icon': 'fa '+item.fa_icon,
                    'tile_color': background_color,
                    'text_color': text_color.replace(';',''),
                    'icon_color': 'color: #1f6abb',
                })
        return data

    def get_shart_data(self, dashboard_obj):
        data = []
        for item in dashboard_obj.items_ids:
            record = request.env[item.model_id.model].sudo().search(eval(item.domain) if item.domain else [])
            res = {}
            if item.item_type != 'tile':
                for r in record:
                    key = eval("r." + item.group_by_field.name)
                    if item.group_by_field.ttype == 'many2one':
                        key = key.name
                    if key in res:
                        res[key] += eval("r." + item.measure_id.name)
                    else:
                        res[key] = eval("r." + item.measure_id.name)
                data.append({
                    'id': item.id,
                    'type': item.item_type,
                    'data': {
                        'labels': list(res.keys()),
                        'datasets': [{
                            'label': item.name,
                            'data': list(res.values()),
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'scales': {'y': {'beginAtZero': 'true'}}
                    }
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

 