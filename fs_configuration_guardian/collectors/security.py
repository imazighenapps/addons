from .base import GuardianCollector


class SecurityCollector(GuardianCollector):
    category = 'security'

    def collect(self):
        items = []

        Privilege = self.env['res.groups.privilege'].sudo()
        for rec in Privilege.search([]):
            data = {
                'name': rec.name,
                'description': rec.description,
                'sequence': rec.sequence,
                'category_id': rec.category_id.id if rec.category_id else False,
                'groups': sorted(rec.group_ids.ids),
            }
            items.append(
                self.item(
                    'res.groups.privilege',
                    rec.id,
                    data,
                    rec.display_name,
                    rec.get_external_id().get(rec.id),
                )
            )

        Group = self.env['res.groups'].sudo()
        for rec in Group.search([]):
            data = {
                'name': rec.name,
                'privilege_id': rec.privilege_id.id if rec.privilege_id else False,
                'implied_ids': sorted(rec.implied_ids.ids),
                'share': rec.share,
                'sequence': rec.sequence,
            }
            items.append(
                self.item(
                    'res.groups',
                    rec.id,
                    data,
                    rec.display_name,
                    rec.get_external_id().get(rec.id),
                )
            )

        User = self.env['res.users'].sudo()
        domain = ['|', ('company_id', '=', self.company.id), ('company_ids', 'in', [self.company.id])]
        for rec in User.search(domain):
            data = {
                'name': rec.name,
                'login': rec.login,
                'active': rec.active,
                'share': rec.share,
                'groups': sorted(rec.group_ids.ids),
                'company_id': rec.company_id.id if rec.company_id else False,
                'company_ids': sorted(rec.company_ids.ids),
            }
            items.append(
                self.item(
                    'res.users',
                    rec.id,
                    data,
                    rec.display_name,
                    rec.get_external_id().get(rec.id),
                )
            )

        ACL = self.env['ir.model.access'].sudo()
        for rec in ACL.search([]):
            data = {
                'name': rec.name,
                'model_id': rec.model_id.id,
                'model': rec.model_id.model,
                'group_id': rec.group_id.id if rec.group_id else False,
                'perm_create': rec.perm_create,
                'perm_read': rec.perm_read,
                'perm_write': rec.perm_write,
                'perm_unlink': rec.perm_unlink,
            }
            items.append(
                self.item(
                    'ir.model.access',
                    rec.id,
                    data,
                    rec.name,
                    rec.get_external_id().get(rec.id),
                )
            )

        Rule = self.env['ir.rule'].sudo()
        for rec in Rule.search([]):
            data = {
                'name': rec.name,
                'model_id': rec.model_id.id,
                'model': rec.model_id.model,
                'groups': sorted(rec.groups.ids),
                'global': getattr(rec, 'global', False),
                'domain_force': rec.domain_force,
                'perm_read': rec.perm_read,
                'perm_write': rec.perm_write,
                'perm_create': rec.perm_create,
                'perm_unlink': rec.perm_unlink,
            }
            items.append(
                self.item(
                    'ir.rule',
                    rec.id,
                    data,
                    rec.name,
                    rec.get_external_id().get(rec.id),
                )
            )

        return items
