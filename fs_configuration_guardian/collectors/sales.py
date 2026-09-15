from .base import GuardianCollector


class SalesCollector(GuardianCollector):
    category = 'sales'

    def collect(self):
        items = []
        specs = [
            ('product.pricelist', ['name', 'currency_id', 'active']),
            ('account.payment.term', ['name', 'active']),
            ('crm.team', ['name', 'company_id', 'active']),
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
                    if hasattr(value, 'id'):
                        value = value.id
                    data[field] = value
                items.append(self.item(model_name, rec.id, data, rec.display_name, rec.get_external_id().get(rec.id)))
        return items
