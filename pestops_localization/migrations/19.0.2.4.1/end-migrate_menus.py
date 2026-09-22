"""Remove the obsolete flat Localization menu (moved under Configuration)."""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('pestops_localization.menu_pestops_localization_root', raise_if_not_found=False)
    if menu:
        menu.unlink()
