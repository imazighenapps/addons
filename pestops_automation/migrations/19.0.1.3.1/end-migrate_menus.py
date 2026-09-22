"""Remove the obsolete flat Automations menu (moved under Configuration)."""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('pestops_automation.menu_pestops_automation_root', raise_if_not_found=False)
    if menu:
        menu.unlink()
