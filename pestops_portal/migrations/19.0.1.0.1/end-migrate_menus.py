"""Remove the obsolete flat Portal menu (moved under Commercial)."""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('pestops_portal.menu_pestops_portal_root', raise_if_not_found=False)
    if menu:
        menu.unlink()
