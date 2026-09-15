import hashlib
import json


class GuardianCollector:
    category = 'technical'

    def __init__(self, env, company):
        self.env = env
        self.company = company

    def collect(self):
        return []

    @staticmethod
    def normalize(value):
        return json.loads(json.dumps(value, sort_keys=True, default=str))

    @staticmethod
    def checksum(value):
        raw = json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    def item(self, model, key, data, label=None, external_id=None):
        normalized = self.normalize(data)
        return {
            'category': self.category,
            'model': model,
            'key': str(key),
            'label': label or str(key),
            'external_id': external_id,
            'data': normalized,
            'checksum': self.checksum(normalized),
        }

    def company_domain(self, model):
        if 'company_id' in model._fields:
            return ['|', ('company_id', '=', self.company.id), ('company_id', '=', False)]
        return []
