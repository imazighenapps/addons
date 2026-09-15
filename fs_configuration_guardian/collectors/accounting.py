from .base import GuardianCollector


class AccountingCollector(GuardianCollector):
    category = 'accounting'

    def collect(self):
        items = []
        specs = [
            ('account.journal', ['name', 'code', 'type', 'company_id', 'active']),
            ('account.tax', ['name', 'amount', 'amount_type', 'type_tax_use', 'company_id', 'active']),
            ('account.fiscal.position', ['name', 'company_id', 'active']),
            ('account.payment.term', ['name', 'company_id', 'active']),
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
