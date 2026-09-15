from .base import GuardianCollector


class InventoryCollector(GuardianCollector):
    category = 'inventory'

    def collect(self):
        items = []
        specs = [
            ('stock.warehouse', ['name', 'code', 'company_id', 'active']),
            ('stock.location', ['name', 'complete_name', 'usage', 'location_id', 'company_id', 'active']),
            ('stock.picking.type', ['name', 'code', 'warehouse_id', 'company_id', 'active']),
            ('stock.route', ['name', 'company_id', 'active', 'product_selectable', 'product_categ_selectable']),
        ]
        for model_name, fields in specs:
            if model_name not in self.env:
                continue
            Model = self.env[model_name].sudo()
            for rec in Model.search(self.company_domain(Model)):
                data = {}
                for field in fields:
                    if field not in Model._fields:
                        continue
                    value = rec[field]
                    if hasattr(value, 'ids'):
                        value = sorted(value.ids)
                    elif hasattr(value, 'id'):
                        value = value.id
                    data[field] = value
                items.append(self.item(model_name, rec.id, data, rec.display_name, rec.get_external_id().get(rec.id)))
        return items
