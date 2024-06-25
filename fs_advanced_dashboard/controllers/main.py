# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http,fields
from odoo.http import  request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)
PERIODES  = {
        "0":"0",
        "today":"yesterday",
        "this_week":"last_week",
        "this_month":"last_month",
        "this_year":"last_year",
        "yesterday":"before_yesterday",
        "last_week":"before_last_week",
        "last_month":"before_last_month",
        "last_two_months":"before_last_two_months",
        "last_three_months":"before_last_three_months",
        "last_year":"before_last_year"
}



    


class Main(http.Controller):



    @http.route('/do/filter/data', auth='user', type='json')
    def do_filter_data(self, **kw):
        data  = kw.get('data')
        period = kw.get('period')
        domain = self.generate_period_domain(period)
        domain_compare = self.generate_period_domain(PERIODES[period])
        data = self.do_filter_data_tiles(data,domain,domain_compare,period)
        data = self.do_filter_data_sharts(data,domain,domain_compare,period)
        return data
    

    def do_filter_data_tiles(self,data,domain,domain_compare,period):
        for tile in data['tiles']:
            tile_obj = request.env['dashboard.item'].sudo().search([("id","=",tile.get('id'))]) 
            records = request.env[tile.get('model')].sudo().search(domain + eval(tile_obj.domain) if tile_obj.domain else domain) 
            records_to_compar = request.env[tile.get('model')].sudo().search(tile.get('domain')+domain_compare) 
            count_field = tile.get('count_field')
            if tile.get('count_type') == 'count':
                value = self.format_value(len(records))
                value_to_compar = self.format_value(len(records_to_compar))
            elif tile.get('count_type') == 'sum':
                value = self.format_value(sum(r[count_field] for r in records))
                value_to_compar = self.format_value(sum(rc[count_field] for rc in records_to_compar))
            elif tile.get('count_type') == 'average':
                value = self.format_value(sum(r[count_field] for r in records) / len(records)) if records else 0
                value_to_compar = self.format_value(sum(rc[count_field] for rc in records_to_compar) / len(records_to_compar)) if records_to_compar else 0
            tile['value'] = value
            tile['objective'] = tile_obj.objective
            tile['value_to_compar'] = value_to_compar
            tile['domain'] = domain + eval(tile_obj.domain) if tile_obj.domain else domain
            float_value             = self.convert_format_to_value(value)
            float_value_to_compar   = self.convert_format_to_value(value_to_compar)
            if period  !='0':
                if float_value_to_compar == 0 and float_value > 0:
                    tile['percentage'] = f"100.00"
                elif float_value_to_compar == 0 and float_value == 0 :   
                    tile['percentage'] = f"0.00"
                else :
                    tile['percentage'] =  f"{(((float_value - float_value_to_compar) / float_value_to_compar) * 100):.2f}%"
            else:
                tile['percentage'] = f"0.00"    
        return data
    
    def do_filter_data_sharts(self,data,domain_filter,domain_compare,period):
        data_filtred = []
        res = data['sharts']
        for shart in res:
            obj = request.env[shart.get('model')].sudo()
            item = request.env['dashboard.item'].sudo().search([('id','=',shart.get('id'))])
            domain  =   domain_filter + eval(item.domain) if item.domain else []
            groupby =  shart.get('groupby')
            measure  =  shart.get('measure')
            result  =   obj.read_group(domain=domain,fields=[measure],groupby=groupby,lazy=False)
            labels = []
            sums = []
            domains=[]
            for r in result:
                domains.append(r.get('__domain'))
                if measure == 'id':
                    sums.append(r.get('__count'))
                else:
                    sums.append(r.get(measure))
                        
                if shart.get('group_by_field_ttype') == 'many2one':
                    mdl = item.group_by_field.relation
                    many2one_id = r.get(groupby)[0] if r.get(groupby) else False
                    name = request.env[mdl].sudo().search([('id','=', many2one_id)]).name
                    labels.append(name)
                else:
                    labels.append(r.get(groupby))
           
            data_filtred.append({
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
        data['sharts'] = data_filtred
        return data

        
    def generate_period_domain(self, selected_option):
        today = fields.Datetime.today()
        if selected_option == "today":
            return [('create_date', '>=', fields.Date.today())]
        elif selected_option == "yesterday":
            return [('create_date', '>=', fields.Date.today() - timedelta(days=1)),('create_date', '<', fields.Date.today())]
        elif selected_option == "this_week":
            return [('create_date', '>=', fields.Date.today() - timedelta(days=fields.Date.today().weekday() + 2))]
        elif selected_option == "last_week":
            return [('create_date', '>=', fields.Date.today() - timedelta(days=fields.Date.today().weekday() + 2 + 7)),
                    ('create_date', '<', fields.Date.today() - timedelta(days=fields.Date.today().weekday() + 2))]
        elif selected_option == "this_month":
            return [('create_date', '>=', fields.Date.today().replace(day=1))]
        elif selected_option == "last_month":
            first_day_last_month = (fields.Date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last_month = fields.Date.today().replace(day=1) - timedelta(days=1)
            return [('create_date', '>=', first_day_last_month), ('create_date', '<=', last_day_last_month)]
        elif selected_option == "last_two_months":
            last_month = (fields.Date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
            two_months_ago = (last_month.replace(day=1) - timedelta(days=1)).replace(day=1)
            return [('create_date', '>=', two_months_ago), ('create_date', '<=', last_month)]
        elif selected_option == "last_three_months":
            last_month = (fields.Date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
            three_months_ago = (last_month.replace(day=1) - timedelta(days=1)).replace(day=1)
            return [('create_date', '>=', three_months_ago), ('create_date', '<=', last_month)]
        elif selected_option == "this_year":
            return [('create_date', '>=', fields.Date.today().replace(month=1, day=1))]
        elif selected_option == "last_year":
            first_day_last_year = (fields.Date.today().replace(year=fields.Date.today().year - 1, month=1, day=1))
            last_day_last_year = (fields.Date.today().replace(year=fields.Date.today().year - 1, month=12, day=31))
            return [('create_date', '>=', first_day_last_year), ('create_date', '<=', last_day_last_year)]
        elif selected_option == "before_yesterday":
            return [('create_date', '=', fields.Date.today() - timedelta(days=2))]
        elif selected_option == "before_last_week":
            return [('create_date', '>=', fields.Date.today() - timedelta(days=fields.Date.today().weekday() + 2 + 14)),
                    ('create_date', '<', fields.Date.today() - timedelta(days=fields.Date.today().weekday() + 2 + 7))]
        elif selected_option == "before_last_month":
            first_day_before_last_month = (fields.Date.today().replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=30)
            last_day_before_last_month = (fields.Date.today().replace(day=1) - timedelta(days=1)) - timedelta(days=30)
            return [('create_date', '>=', first_day_before_last_month), ('create_date', '<=', last_day_before_last_month)]
        elif selected_option == "before_last_two_months":
            last_month_before_last = (fields.Date.today().replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=30)
            two_months_ago_before_last = (last_month_before_last.replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=30)
            return [('create_date', '>=', two_months_ago_before_last), ('create_date', '<=', last_month_before_last)]
        elif selected_option == "before_last_three_months":
            last_month_before_last = (fields.Date.today().replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=30)
            three_months_ago_before_last = (last_month_before_last.replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=30)
            return [('create_date', '>=', three_months_ago_before_last), ('create_date', '<=', last_month_before_last)]
        elif selected_option == "before_last_year":
            first_day_before_last_year = (fields.Date.today().replace(year=fields.Date.today().year - 2, month=1, day=1))
            last_day_before_last_year = (fields.Date.today().replace(year=fields.Date.today().year - 2, month=12, day=31))
            return [('create_date', '>=', first_day_before_last_year), ('create_date', '<=', last_day_before_last_year)]
        else:
            return []
        

    def format_value(self,value):
        val = value
        magnitude = 0
        while abs(value) >= 1000:
            magnitude += 1
            value /= 1000.0
            val = '%.2f%s' % (value, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
        return val
    

    def convert_format_to_value(self,formatted_value):
        if isinstance(formatted_value, int) or isinstance(formatted_value, float):
            return formatted_value
        else:
            suffixes = {'K': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15}
            magnitude = 0
            while formatted_value and formatted_value[-1] in suffixes:
                magnitude += 1
                formatted_value = formatted_value[:-1]
            try:
                real_value = float(formatted_value)
            except ValueError:
                raise ValueError("Invalid value format")
            real_value *= suffixes.get(formatted_value[-1], 1)
            return real_value