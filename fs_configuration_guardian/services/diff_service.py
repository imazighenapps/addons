from .risk_service import assess


class GuardianDiffService:
    def __init__(self, env):
        self.env = env

    @staticmethod
    def _index(payload):
        return {(i.get('category'), i.get('model'), i.get('key')): i for i in payload.get('items', []) if not i.get('collector_error')}

    def compare(self, baseline_snapshot, current_snapshot):
        before = self._index(baseline_snapshot.payload or {})
        after = self._index(current_snapshot.payload or {})
        changes = []
        for key in sorted(set(before) | set(after)):
            old = before.get(key)
            new = after.get(key)
            if old and not new:
                operation = 'removed'
                item = old
            elif new and not old:
                operation = 'added'
                item = new
            elif old.get('checksum') != new.get('checksum'):
                operation = 'modified'
                item = new
            else:
                continue
            changes.append({
                'item': item,
                'before': old.get('data') if old else {},
                'after': new.get('data') if new else {},
                'operation': operation,
                'risk': assess(item, operation),
            })
        return changes
