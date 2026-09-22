"""Remove the obsolete flat Proof menu (moved under Operations)."""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('pestops_proof.menu_pestops_proof_root', raise_if_not_found=False)
    if menu:
        menu.unlink()
