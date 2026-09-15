CRITICAL_MODELS = {'res.users', 'res.groups', 'ir.model.access', 'ir.rule'}
HIGH_MODELS = {'base.automation', 'ir.cron', 'ir.actions.server'}
ACCOUNTING_MODELS = {'account.tax', 'account.journal', 'account.fiscal.position', 'account.payment.term'}


def assess(item, operation):
    model = item.get('model')
    category = item.get('category')
    if model in CRITICAL_MODELS:
        return {'level': 'critical', 'reason': 'Security configuration changed.'}
    if category == 'automation' or model in HIGH_MODELS:
        return {'level': 'high', 'reason': 'Automation behavior can change operational processes.'}
    if model in ACCOUNTING_MODELS:
        return {'level': 'critical', 'reason': 'Accounting configuration can affect financial processing.'}
    if category in ('inventory', 'sales'):
        return {'level': 'medium', 'reason': 'Operational configuration changed.'}
    if category == 'studio':
        return {'level': 'medium', 'reason': 'Studio customization changed.'}
    return {'level': 'low', 'reason': 'Technical configuration changed.'}
