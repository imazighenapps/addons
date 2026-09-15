from .base import GuardianCollector


class AutomationCollector(GuardianCollector):
    category = 'automation'

    def collect(self):
        items = []
        for model_name in ('base.automation', 'ir.cron', 'ir.actions.server'):
            if model_name not in self.env:
                continue
            Model = self.env[model_name].sudo()
            for rec in Model.search([]):
                data = {}
                for field in Model._fields:
                    if field in ('create_uid', 'create_date', 'write_uid', 'write_date'):
                        continue
                    field_obj = Model._fields[field]
                    if not field_obj.store:
                        continue
                    try:
                        value = rec[field]
                        if hasattr(value, 'ids'):
                            value = sorted(value.ids)
                        elif hasattr(value, 'id'):
                            value = value.id
                        elif hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        elif isinstance(value, (str, int, float, bool, type(None), list, dict)):
                            pass
                        else:
                            value = str(value)
                        data[field] = value
                    except Exception:
                        continue
                label = getattr(rec, 'name', False) or rec.display_name
                items.append(self.item(model_name, rec.id, data, label, rec.get_external_id().get(rec.id)))
        return items
