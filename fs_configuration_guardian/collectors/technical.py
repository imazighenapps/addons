from .base import GuardianCollector


class TechnicalCollector(GuardianCollector):
    category = 'technical'

    def collect(self):
        items = []
        Module = self.env['ir.module.module'].sudo()
        for rec in Module.search([('state', 'in', ('installed', 'to upgrade'))]):
            data = {'name': rec.name, 'state': rec.state, 'latest_version': rec.latest_version}
            items.append(self.item('ir.module.module', rec.id, data, rec.shortdesc or rec.name, rec.get_external_id().get(rec.id)))

        View = self.env['ir.ui.view'].sudo()
        for rec in View.search([]):
            data = {'name': rec.name, 'model': rec.model, 'type': rec.type, 'priority': rec.priority, 'active': rec.active, 'inherit_id': rec.inherit_id.id if rec.inherit_id else False}
            data['arch'] = rec.arch
            items.append(self.item('ir.ui.view', rec.id, data, rec.name, rec.get_external_id().get(rec.id)))
        return items
