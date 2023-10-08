from . import models
from . import controllers

import logging
from odoo import api, SUPERUSER_ID
_logger = logging.getLogger(__name__)



def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    actions_to_clean = env['ir.actions.client'].search([('tag','=','dashboard_show')])
    for action in actions_to_clean:
        menu_to_clean = env['ir.ui.menu'].search([('action','=','ir.actions.client,'+str(action.id))]) 
        menu_to_clean.unlink()
    actions_to_clean.unlink()
