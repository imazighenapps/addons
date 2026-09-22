"""Remove the obsolete flat Billing menu (moved under Commercial)."""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('pestops_account.menu_pestops_billing', raise_if_not_found=False)
    if menu:
        menu.unlink()
