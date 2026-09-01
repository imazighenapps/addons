# -*- coding: utf-8 -*-
from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        users._eduflow_sync_parent_portal_group()
        return users

    def write(self, vals):
        res = super().write(vals)
        if 'partner_id' in vals:
            self._eduflow_sync_parent_portal_group()
        return res

    def _eduflow_sync_parent_portal_group(self):
        """Automatically add the 'Parent (portal)' group to any user
        linked to the contact of an existing eduflow.parent record.

        This covers the standard Odoo flow "Actions > Grant Access to
        portal" from the contact form, which does not know our groups
        and would otherwise only add base.group_portal: without this
        synchronization, the parent would end up with a portal account
        active but no rights on eduflow.* models (empty portal,
        404 errors on all parent portal pages)."""
        group = self.env.ref('eduflow.group_eduflow_parent_portal', raise_if_not_found=False)
        if not group:
            return
        Parent = self.env['eduflow.parent'].sudo()
        for user in self:
            if not user.partner_id:
                continue
            parent = Parent.search([('partner_id', '=', user.partner_id.id)], limit=1)
            if parent:
                if group.id not in user.groups_id.ids:
                    user.sudo().write({'groups_id': [(4, group.id)]})
                if not parent.portal_access:
                    parent.portal_access = True
