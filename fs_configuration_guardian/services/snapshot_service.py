import hashlib
import json

from ..collectors.accounting import AccountingCollector
from ..collectors.automation import AutomationCollector
from ..collectors.inventory import InventoryCollector
from ..collectors.sales import SalesCollector
from ..collectors.security import SecurityCollector
from ..collectors.studio import StudioCollector
from ..collectors.technical import TechnicalCollector


class GuardianSnapshotService:
    def __init__(self, env):
        self.env = env

    def capture(self, company=None):
        company = company or self.env.company
        collectors = [
            SecurityCollector(self.env, company),
            AutomationCollector(self.env, company),
            StudioCollector(self.env, company),
            AccountingCollector(self.env, company),
            InventoryCollector(self.env, company),
            SalesCollector(self.env, company),
            TechnicalCollector(self.env, company),
        ]
        items = []
        for collector in collectors:
            try:
                items.extend(collector.collect())
            except Exception as exc:
                items.append({
                    'category': collector.category,
                    'model': '__collector__',
                    'key': collector.__class__.__name__,
                    'label': collector.__class__.__name__,
                    'external_id': None,
                    'data': {'error': str(exc)},
                    'checksum': '',
                    'collector_error': True,
                })
        payload = {'company_id': company.id, 'items': items}
        raw = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str).encode()
        return {'payload': payload, 'item_count': len(items), 'checksum': hashlib.sha256(raw).hexdigest()}
