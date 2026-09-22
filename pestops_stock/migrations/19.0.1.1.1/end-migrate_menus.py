"""Remove the obsolete flat Stock menu (moved under Resources)."""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('pestops_stock.menu_pestops_stock', raise_if_not_found=False)
    if menu:
        menu.unlink()
