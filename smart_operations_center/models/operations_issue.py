from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SmartOperationsIssue(models.Model):
    _name = 'smart.operations.issue'
    _description = 'Operational Issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'risk_score desc, detected_at desc, id desc'

    name = fields.Char(required=True, default=lambda self: _('New'), copy=False, readonly=True)
    active = fields.Boolean(default=True)
    issue_type = fields.Selection([
        ('delay', 'Delay'), ('stagnation', 'Stagnation'),
        ('deadline_risk', 'Deadline Risk'), ('dependency', 'Dependency'),
        ('missing_action', 'Missing Action'), ('process_degradation', 'Process Degradation'),
        ('business_risk', 'Business Risk'),
    ], required=True, tracking=True)
    severity = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical'),
    ], default='medium', required=True, tracking=True)
    state = fields.Selection([
        ('new', 'New'), ('investigating', 'Investigating'), ('action_required', 'Action Required'),
        ('escalated', 'Escalated'), ('resolved', 'Resolved'), ('ignored', 'Ignored'), ('snoozed', 'Snoozed'),
    ], default='new', required=True, tracking=True)
    root_model_id = fields.Many2one('ir.model', string='Root Model', ondelete='set null')
    root_res_id = fields.Integer(string='Root Record ID')
    root_reference = fields.Char(compute='_compute_root_reference', store=True)
    root_cause_model_id = fields.Many2one('ir.model', string='Root Cause Model', ondelete='set null')
    root_cause_res_id = fields.Integer(string='Root Cause Record ID')
    process_id = fields.Many2one('smart.operations.process', ondelete='set null')
    rule_id = fields.Many2one('smart.operations.rule', ondelete='set null')
    responsible_id = fields.Many2one('res.users', tracking=True, ondelete='set null')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    detected_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    due_date = fields.Datetime(index=True)
    resolved_at = fields.Datetime(readonly=True)
    resolution_duration_hours = fields.Float(compute='_compute_resolution_duration', store=True)
    delay_days = fields.Float(default=0.0)
    risk_score = fields.Float(default=0.0, tracking=True, index=True)
    risk_explanation = fields.Text()
    business_impact = fields.Monetary(currency_field='currency_id', default=0.0, tracking=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True)
    affected_customer_count = fields.Integer(default=0)
    affected_order_count = fields.Integer(default=0)
    affected_delivery_count = fields.Integer(default=0)
    affected_manufacturing_count = fields.Integer(default=0)
    affected_purchase_count = fields.Integer(default=0)
    affected_quantity = fields.Float(default=0.0)
    impact_summary = fields.Text()
    impact_path = fields.Text(help='Explainable business-impact chain from the root record to affected records.')
    root_cause_reference = fields.Char(compute='_compute_root_cause_reference', store=True)
    action_ids = fields.One2many('smart.operations.action', 'issue_id')
    impact_ids = fields.One2many('smart.operations.impact', 'issue_id', string='Impact Records', copy=False)
    action_count = fields.Integer(compute='_compute_counts')
    escalation_count = fields.Integer(compute='_compute_counts')
    snoozed_until = fields.Datetime()
    resolution_reason = fields.Text()
    resolution_notes = fields.Text()

    @api.depends('root_cause_model_id', 'root_cause_res_id')
    def _compute_root_cause_reference(self):
        for issue in self:
            issue.root_cause_reference = False
            if issue.root_cause_model_id and issue.root_cause_res_id:
                try:
                    record = self.env[issue.root_cause_model_id.model].browse(issue.root_cause_res_id).exists()
                    issue.root_cause_reference = record.display_name if record else f'{issue.root_cause_model_id.name} #{issue.root_cause_res_id}'
                except (KeyError, ValueError):
                    issue.root_cause_reference = f'{issue.root_cause_model_id.name} #{issue.root_cause_res_id}'

    @api.depends('root_model_id', 'root_res_id')
    def _compute_root_reference(self):
        for issue in self:
            if issue.root_model_id and issue.root_res_id:
                try:
                    record = self.env[issue.root_model_id.model].browse(issue.root_res_id).exists()
                    issue.root_reference = record.display_name if record else f'{issue.root_model_id.name} #{issue.root_res_id}'
                except (KeyError, ValueError):
                    issue.root_reference = f'{issue.root_model_id.name} #{issue.root_res_id}'
            else:
                issue.root_reference = False

    @api.depends('action_ids', 'action_ids.state')
    def _compute_counts(self):
        for issue in self:
            issue.action_count = len(issue.action_ids)
            issue.escalation_count = len(issue.action_ids.filtered(lambda a: a.action_type == 'escalate'))

    @api.depends('detected_at', 'resolved_at')
    def _compute_resolution_duration(self):
        for issue in self:
            end = issue.resolved_at or fields.Datetime.now()
            issue.resolution_duration_hours = max((end - issue.detected_at).total_seconds() / 3600.0, 0.0) if issue.detected_at else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('smart.operations.issue') or _('New')
        records = super().create(vals_list)
        for record in records:
            record.message_post(body=_('Operational issue detected with risk score %.1f.') % record.risk_score)
        return records

    def action_investigate(self):
        self.ensure_one()
        if self.state in ('resolved', 'ignored'):
            raise UserError(_('A resolved or ignored issue cannot be investigated.'))
        self.state = 'investigating'
        return {
            'type': 'ir.actions.act_window', 'name': _('Investigate Issue'),
            'res_model': 'smart.operations.investigate.wizard', 'view_mode': 'form',
            'target': 'new', 'context': {'default_issue_id': self.id},
        }

    def action_resolve(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window', 'name': _('Resolve Issue'),
            'res_model': 'smart.operations.resolve.wizard', 'view_mode': 'form',
            'target': 'new', 'context': {'default_issue_id': self.id},
        }

    def action_open_root_record(self):
        self.ensure_one()
        if not self.root_model_id or not self.root_res_id:
            raise UserError(_('No root record is linked to this issue.'))
        record = self.env[self.root_model_id.model].browse(self.root_res_id).exists()
        if not record:
            raise UserError(_('The linked root record no longer exists.'))
        return {'type': 'ir.actions.act_window', 'name': record.display_name, 'res_model': record._name,
                'views': [(False, 'form')], 'res_id': record.id, 'target': 'current'}

    def action_mark_action_required(self):
        self.write({'state': 'action_required'})

    def action_snooze(self):
        self.write({'state': 'snoozed', 'snoozed_until': fields.Datetime.now() + timedelta(hours=24)})

    def action_ignore(self):
        self.write({'state': 'ignored', 'resolved_at': fields.Datetime.now()})

    @api.model
    def get_dashboard_data(self):
        today = fields.Date.context_today(self)
        now = fields.Datetime.now()
        week_start = today - timedelta(days=6)
        Action = self.env['smart.operations.action']
        Baseline = self.env['smart.operations.baseline']
        open_issues = self.search([('state', 'not in', ('resolved', 'ignored'))])
        sev_defs = [('critical', 'Critical', 'red'), ('high', 'High', 'orange'),
                    ('medium', 'Medium', 'amber'), ('low', 'Low', 'green')]
        by_severity = [
            {'label': label, 'value': len(open_issues.filtered(lambda r, _k=key: r.severity == _k)), 'tone': tone}
            for key, label, tone in sev_defs
        ]
        state_defs = [('new', 'New', 'blue'), ('investigating', 'Investigating', 'violet'),
                      ('action_required', 'Action Required', 'amber'), ('escalated', 'Escalated', 'red')]
        by_state = [
            {'label': label, 'value': len(open_issues.filtered(lambda r, _k=key: r.state == _k)), 'tone': tone}
            for key, label, tone in state_defs
        ]
        type_defs = [('delay', 'Delay'), ('stagnation', 'Stagnation'), ('deadline_risk', 'Deadline Risk'),
                     ('dependency', 'Dependency'), ('missing_action', 'Missing Action'),
                     ('process_degradation', 'Process Degradation'), ('business_risk', 'Business Risk')]
        impact_by_type = []
        for key, label in type_defs:
            total = sum(open_issues.filtered(lambda r, _k=key: r.issue_type == _k).mapped('business_impact'))
            if total:
                impact_by_type.append({'label': label, 'value': total})
        impact_by_type = sorted(impact_by_type, key=lambda x: x['value'], reverse=True)[:6]
        activity = []
        for back in range(6, -1, -1):
            day = today - timedelta(days=back)
            day_start = '%s 00:00:00' % day
            day_end = '%s 00:00:00' % (day + timedelta(days=1))
            activity.append({
                'label': day.strftime('%a %d'),
                'detected': self.search_count([('detected_at', '>=', day_start), ('detected_at', '<', day_end)]),
                'resolved': self.search_count([('state', '=', 'resolved'), ('resolved_at', '>=', day_start), ('resolved_at', '<', day_end)]),
            })
        top = open_issues.sorted(key=lambda r: (r.risk_score or 0.0), reverse=True)[:8]
        overdue = Action.search(
            [('state', '=', 'pending'), ('due_date', '!=', False), ('due_date', '<', now)],
            order='due_date asc', limit=8)
        baselines = Baseline.search(
            [('health', 'in', ['watch', 'critical'])], order='deviation_percent desc', limit=8)
        risks = open_issues.mapped('risk_score')
        return {
            'open_count': len(open_issues),
            'critical_count': len(open_issues.filtered(lambda r: r.severity == 'critical')),
            'escalated_count': len(open_issues.filtered(lambda r: r.state == 'escalated')),
            'snoozed_count': len(open_issues.filtered(lambda r: r.state == 'snoozed')),
            'overdue_actions': len(Action.search(
                [('state', '=', 'pending'), ('due_date', '!=', False), ('due_date', '<', now)])),
            'resolved_week': self.search_count([
                ('state', '=', 'resolved'),
                ('resolved_at', '>=', '%s 00:00:00' % week_start)]),
            'avg_risk': round(sum(risks) / len(risks), 1) if risks else 0.0,
            'total_impact': sum(open_issues.mapped('business_impact')),
            'by_severity': by_severity,
            'by_state': by_state,
            'impact_by_type': impact_by_type,
            'activity': activity,
            'top_issues': [{
                'id': r.id, 'name': r.name or '',
                'severity': dict(r._fields['severity'].selection).get(r.severity, ''),
                'state': dict(r._fields['state'].selection).get(r.state, ''),
                'risk': r.risk_score or 0.0, 'impact': r.business_impact or 0.0,
                'root': r.root_reference or '',
            } for r in top],
            'overdue_list': [{
                'id': a.issue_id.id if a.issue_id else False, 'name': a.name or '',
                'issue': a.issue_id.display_name if a.issue_id else '',
                'due': fields.Datetime.to_string(a.due_date)[:16] if a.due_date else '',
                'responsible': a.responsible_id.display_name or '',
            } for a in overdue],
            'baselines': [{
                'id': b.id, 'process': b.process_id.display_name if b.process_id else '',
                'average': b.average_days or 0.0, 'p90': b.p90_days or 0.0,
                'current': b.current_days or 0.0, 'deviation': b.deviation_percent or 0.0,
                'health': dict(b._fields['health'].selection).get(b.health, ''),
            } for b in baselines],
        }

    @api.model
    def _cron_reactivate_snoozed(self):
        self.search([
            ('state', '=', 'snoozed'),
            ('snoozed_until', '<=', fields.Datetime.now()),
        ]).write({'state': 'new', 'snoozed_until': False})

    @api.model
    def _cron_process_escalations(self):
        now = fields.Datetime.now()
        actions = self.env['smart.operations.action'].search([
            ('action_type', '=', 'escalate'),
            ('state', '=', 'pending'),
            ('due_date', '<=', now),
        ], limit=300)
        for action in actions:
            issue = action.issue_id
            if not issue or issue.state in ('resolved', 'ignored'):
                action.write({'state': 'cancelled'})
                continue
            responsible = action.responsible_id
            policy = action.escalation_policy_id
            if responsible:
                issue.write({'responsible_id': responsible.id, 'state': 'escalated'})
                if issue.message_follower_ids and responsible.partner_id:
                    issue.message_subscribe(partner_ids=[responsible.partner_id.id])
                if not policy or policy.notify_activity:
                    issue.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=responsible.id,
                        summary=_('Escalated operational issue'),
                        note=_('Issue %s requires attention. Risk score: %.1f.') % (issue.name, issue.risk_score),
                    )
            if policy and action.escalation_level == 1 and policy.second_user_id and policy.second_delay_hours:
                second_due = issue.detected_at + timedelta(hours=policy.second_delay_hours)
                already_created = self.env['smart.operations.action'].search_count([
                    ('issue_id', '=', issue.id),
                    ('escalation_policy_id', '=', policy.id),
                    ('escalation_level', '=', 2),
                    ('state', '!=', 'cancelled'),
                ])
                if not already_created:
                    self.env['smart.operations.action'].create({
                        'name': _('Second escalation: %s') % issue.name,
                        'issue_id': issue.id,
                        'action_type': 'escalate',
                        'responsible_id': policy.second_user_id.id,
                        'due_date': second_due,
                        'notes': _('Second-level escalation generated automatically.'),
                        'escalation_policy_id': policy.id,
                        'escalation_level': 2,
                    })
            action.action_complete()
        return True
