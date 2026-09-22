"""Remove the obsolete flat Production menu (moved under Configuration)."""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('pestops_hardening.menu_pestops_hardening_root', raise_if_not_found=False)
    if menu:
        menu.unlink()
