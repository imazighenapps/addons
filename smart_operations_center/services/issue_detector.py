import ast
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from ..hooks import sync_default_rules


class SmartOperationsIssueDetector(models.AbstractModel):
    _name = 'smart.operations.issue.detector'
    _description = 'Operational Issue Detector'

    @api.model
    def _safe_domain(self, value):
        """Parse a restricted Odoo domain and resolve supported date tokens.

        Rule configuration is data, never executable Python. Supported tokens are
        ``today``, ``today-Nd``, ``now`` and ``now-NNh``.
        """
        try:
            parsed = ast.literal_eval(value or '[]')
        except (ValueError, SyntaxError) as exc:
            raise UserError(_('Invalid monitoring domain. Use a valid Odoo domain list.')) from exc
        if not isinstance(parsed, list):
            raise UserError(_('A monitoring domain must be a list.'))
        return self._resolve_domain_values(parsed)

    @api.model
    def _resolve_domain_values(self, node):
        if isinstance(node, list):
            return [self._resolve_domain_values(item) for item in node]
        if isinstance(node, tuple):
            return tuple(self._resolve_domain_values(item) for item in node)
        if isinstance(node, str):
            value = node.strip().lower()
            if value == 'today':
                return fields.Date.context_today(self)
            if value == 'now':
                return fields.Datetime.now()
            if value.startswith('today-') and value.endswith('d'):
                try:
                    days = int(value[6:-1])
                    return fields.Date.context_today(self) - timedelta(days=days)
                except ValueError:
                    pass
            if value.startswith('now-') and value.endswith('h'):
                try:
                    hours = int(value[4:-1])
                    return fields.Datetime.now() - timedelta(hours=hours)
                except ValueError:
                    pass
        return node

    @api.model
    def run_rules(self, limit_per_rule=200):
        sync_default_rules(self.env)
        Issue = self.env['smart.operations.issue']
        rules = self.env['smart.operations.rule'].search(
            [('active', '=', True)], order='sequence, id'
        )
        created = Issue.browse()
        for rule in rules:
            model = self.env.get(rule.model_id.model)
            if not model:
                continue
            domain = self._safe_domain(rule.domain)
            if 'company_id' in model._fields:
                domain.append(('company_id', 'in', self.env.companies.ids))
            max_records = min(rule.max_records_per_run or limit_per_rule, limit_per_rule)
            records = model.search(domain, limit=max_records)
            for record in records:
                if self._issue_exists(rule, record):
                    continue
                delay_days = self._estimate_delay(record, rule.date_field)
                impact = self.env['smart.operations.impact.engine'].analyze(record)
                score, factors = self.env['smart.operations.risk.engine'].calculate(
                    delay_days=delay_days,
                    impact=impact['business_impact'],
                    customer_count=len(impact['customers']),
                    dependency_count=impact['dependency_count'],
                    rule_weight=rule.risk_weight,
                )
                severity = self._severity_from_score(score, rule.severity)
                root_cause = impact.get('root_cause') or record
                root_cause_model = self.env['ir.model'].search(
                    [('model', '=', root_cause._name)], limit=1
                )
                company = record.company_id if 'company_id' in record._fields and record.company_id else self.env.company
                issue = Issue.create({
                    'issue_type': rule.rule_issue_type,
                    'severity': severity,
                    'root_model_id': rule.model_id.id,
                    'root_res_id': record.id,
                    'root_cause_model_id': root_cause_model.id,
                    'root_cause_res_id': root_cause.id,
                    'rule_id': rule.id,
                    'responsible_id': rule.responsible_id.id or self.env.user.id,
                    'company_id': company.id,
                    'delay_days': delay_days,
                    'risk_score': score,
                    'risk_explanation': self._risk_explanation(factors),
                    'business_impact': impact['business_impact'],
                    'affected_customer_count': len(impact['customers']),
                    'affected_order_count': len(impact['orders']),
                    'affected_delivery_count': len(impact['deliveries']),
                    'affected_manufacturing_count': len(impact['manufacturing']),
                    'affected_purchase_count': len(impact['purchases']),
                    'affected_quantity': impact['quantity'],
                    'impact_summary': self._impact_summary(impact),
                    'impact_path': '\n'.join(impact.get('path', [])),
                })
                self._create_impact_snapshots(issue, impact)
                self._create_rule_actions(rule, issue)
                created |= issue
        return created

    def _issue_exists(self, rule, record):
        return bool(self.env['smart.operations.issue'].search_count([
            ('rule_id', '=', rule.id),
            ('root_model_id', '=', rule.model_id.id),
            ('root_res_id', '=', record.id),
            ('state', 'not in', ('resolved', 'ignored')),
        ]))


    @api.model
    def _create_impact_snapshots(self, issue, impact):
        Impact = self.env['smart.operations.impact']
        model_cache = {}
        values_list = []
        relation_map = {
            'customer': 'customer',
            'sales_order': 'sales_order',
            'delivery': 'delivery',
            'manufacturing': 'manufacturing',
            'purchase': 'purchase',
        }
        for relation_type, records in impact.get('impact_records', {}).items():
            for item in list(records.values())[:100]:
                record = item['record']
                model = model_cache.get(record._name)
                if model is None:
                    model = self.env['ir.model'].search([('model', '=', record._name)], limit=1)
                    model_cache[record._name] = model
                if not model:
                    continue
                values_list.append({
                    'issue_id': issue.id,
                    'model_id': model.id,
                    'res_id': record.id,
                    'relation_type': relation_map.get(relation_type, 'other'),
                    'quantity': item.get('quantity', 0.0),
                    'monetary_value': item.get('monetary_value', 0.0),
                })
        if values_list:
            Impact.create(values_list)

    def _create_rule_actions(self, rule, issue):
        Action = self.env['smart.operations.action']
        if rule.action_create_activity and issue.responsible_id:
            Action.create({
                'name': _('Investigate: %s') % issue.name,
                'issue_id': issue.id,
                'action_type': 'activity',
                'responsible_id': issue.responsible_id.id,
                'due_date': fields.Datetime.now() + timedelta(hours=rule.activity_due_hours),
            })
        if rule.escalation_policy_id:
            Action.create({
                'name': _('Escalation policy: %s') % rule.escalation_policy_id.name,
                'issue_id': issue.id,
                'action_type': 'escalate',
                'responsible_id': rule.escalation_policy_id.first_user_id.id or issue.responsible_id.id,
                'due_date': fields.Datetime.now() + timedelta(hours=rule.escalation_policy_id.first_delay_hours),
                'notes': _('Automatic escalation policy attached to this issue.'),
                'escalation_policy_id': rule.escalation_policy_id.id,
                'escalation_level': 1,
            })

    @api.model
    def _estimate_delay(self, record, configured_field=False):
        field_names = [configured_field] if configured_field else []
        field_names += ['date_deadline', 'date_planned', 'commitment_date', 'scheduled_date', 'invoice_date_due']
        for field_name in dict.fromkeys(field_names):
            if field_name and field_name in record._fields:
                value = record[field_name]
                if value:
                    value = fields.Datetime.to_datetime(value)
                    return max((fields.Datetime.now() - value).total_seconds() / 86400.0, 0.0)
        return 0.0

    @staticmethod
    def _severity_from_score(score, minimum):
        ordered = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        calculated = 'critical' if score >= 75 else 'high' if score >= 50 else 'medium' if score >= 25 else 'low'
        return calculated if ordered[calculated] >= ordered[minimum] else minimum

    @staticmethod
    def _risk_explanation(factors):
        return ', '.join(
            f'{key.replace("_", " ").title()}: {value:.1f}'
            for key, value in factors.items()
        )

    @staticmethod
    def _impact_summary(impact):
        return _(
            '%(customers)s customer(s), %(orders)s sales order(s), '
            '%(deliveries)s delivery(ies), %(manufacturing)s manufacturing order(s), '
            '%(purchases)s purchase order(s), %(quantity).2f units and %(amount).2f monetary impact.'
        ) % {
            'customers': len(impact['customers']),
            'orders': len(impact['orders']),
            'deliveries': len(impact['deliveries']),
            'manufacturing': len(impact['manufacturing']),
            'purchases': len(impact['purchases']),
            'quantity': impact['quantity'],
            'amount': impact['business_impact'],
        }

    @api.model
    def _cron_detect_issues(self):
        self.run_rules()
        self.env['smart.operations.issue']._cron_reactivate_snoozed()
        self.env['smart.operations.issue']._cron_process_escalations()
