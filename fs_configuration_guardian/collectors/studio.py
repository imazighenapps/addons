from .base import GuardianCollector


class StudioCollector(GuardianCollector):
    category = 'studio'

    def collect(self):
        items = []
        View = self.env['ir.ui.view'].sudo()
        for rec in View.search([('mode', '=', 'extension')]):
            xmlid = rec.get_external_id().get(rec.id)
            if xmlid and xmlid.startswith('studio_customization.'):
                data = {
                    'name': rec.name,
                    'model': rec.model,
                    'type': rec.type,
                    'priority': rec.priority,
                    'inherit_id': rec.inherit_id.id if rec.inherit_id else False,
                    'arch': rec.arch,
                    'active': rec.active,
                }
                items.append(self.item('ir.ui.view', rec.id, data, rec.name, xmlid))
        if 'ir.model.fields' in self.env:
            Field = self.env['ir.model.fields'].sudo()
            for rec in Field.search([]):
                xmlid = rec.get_external_id().get(rec.id)
                if xmlid and xmlid.startswith('studio_customization.'):
                    data = {
                        'name': rec.name,
                        'field_description': rec.field_description,
                        'model': rec.model,
                        'ttype': rec.ttype,
                        'required': rec.required,
                        'readonly': rec.readonly,
                        'store': rec.store,
                        'index': rec.index,
                    }
                    items.append(self.item('ir.model.fields', rec.id, data, rec.field_description or rec.name, xmlid))
        return items
