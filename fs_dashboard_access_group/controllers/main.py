# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)


from odoo.addons.fs_dashboard.controllers.main import Main

class MainInherit(Main):
    
    def get_tiles_data(self, dashboard_obj):
        res = super(MainInherit, self).get_tiles_data(dashboard_obj)

        for data in res :
            id = data['id']
            item = request.env['dashboard.item'].search([('id','=',id)])
            if item.user_ids:
               if request.env.user.id not in item.user_ids.ids :
                    res.remove(data)
        return res

    def get_shart_data(self, dashboard_obj):
        res = super(MainInherit, self).get_shart_data(dashboard_obj)
        _logger.warning('\n ok ok res =>%s',res)
        for data in res :
            id = data['id']
            item = request.env['dashboard.item'].search([('id','=',id)])
            if item.user_ids:
               if request.env.user.id not in item.user_ids.ids :
                    res.remove(data)
        return res

      