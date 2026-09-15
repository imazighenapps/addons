from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GuardianBaseline(models.Model):
    _name = 'fs.guardian.baseline'
    _description = 'Configuration Guardian Baseline'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    description = fields.Text()
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')], default='draft', required=True, tracking=True)
    snapshot_id = fields.Many2one('fs.guardian.snapshot', readonly=True, copy=False)
    snapshot_count = fields.Integer(compute='_compute_snapshot_count')
    change_count = fields.Integer(compute='_compute_change_count')
    critical_count = fields.Integer(compute='_compute_health_metrics')
    high_count = fields.Integer(compute='_compute_health_metrics')
    medium_count = fields.Integer(compute='_compute_health_metrics')
    health_score = fields.Integer(compute='_compute_health_metrics')
    last_scan_at = fields.Datetime(compute='_compute_health_metrics')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'A baseline with this name already exists for this company.'),
    ]

    @api.depends('snapshot_id')
    def _compute_snapshot_count(self):
        for record in self:
            record.snapshot_count = 1 if record.snapshot_id else 0

    def _compute_change_count(self):
        Change = self.env['fs.guardian.change']
        for record in self:
            record.change_count = Change.search_count([('baseline_id', '=', record.id)])

    def _compute_health_metrics(self):
        Change = self.env['fs.guardian.change']
        for record in self:
            changes = Change.search([('baseline_id', '=', record.id), ('status', '=', 'unknown')])
            critical = sum(change.risk_level == 'critical' for change in changes)
            high = sum(change.risk_level == 'high' for change in changes)
            medium = sum(change.risk_level == 'medium' for change in changes)
            penalty = critical * 20 + high * 8 + medium * 2
            record.critical_count = critical
            record.high_count = high
            record.medium_count = medium
            record.health_score = max(0, 100 - penalty)
            last = Change.search([('baseline_id', '=', record.id)], order='detected_at desc', limit=1)
            record.last_scan_at = last.detected_at if last else False

    def action_create_snapshot(self):
        self.ensure_one()
        snapshot = self.env['fs.guardian.snapshot'].create_from_current(self, is_baseline=True)
        self.snapshot_id = snapshot.id
        self.state = 'active'
        self.message_post(body=_('Production baseline created from snapshot %s.') % snapshot.display_name)
        return snapshot.action_view_form()

    def action_archive_baseline(self):
        for record in self:
            record.state = 'archived'
            record.active = False

    def action_reactivate(self):
        for record in self:
            record.active = True
            record.state = 'active'

    @api.model
    def cron_scan_active_baselines(self):
        from ..services.diff_service import GuardianDiffService
        for baseline in self.search([('state', '=', 'active')], order='id'):
            if not baseline.snapshot_id:
                continue
            snapshot = self.env['fs.guardian.snapshot'].create_from_current(baseline, is_baseline=False)
            changes = GuardianDiffService(self.env).compare(baseline.snapshot_id, snapshot)
            Change = self.env['fs.guardian.change']
            new_changes = self.env['fs.guardian.change']
            for change in changes:
                detected = Change.create_change(baseline, change['item'], change['before'], change['after'], change['operation'], change['risk'])
                if detected.create_date == detected.write_date:
                    new_changes |= detected
            if new_changes:
                critical = new_changes.filtered(lambda c: c.risk_level == 'critical')
                body = _('%s new configuration changes detected. Critical: %s.') % (len(new_changes), len(critical))
                baseline.message_post(body=body, subtype_xmlid='mail.mt_note')
                baseline.activity_schedule('mail.mail_activity_data_todo', summary=_('Review configuration drift'), note=body)
        return True

    def action_scan_now(self):
        self.ensure_one()
        if self.state != 'active' or not self.snapshot_id:
            raise UserError(_('Only an active baseline with a production snapshot can be scanned.'))
        return self.action_open_scan_wizard()

    def action_open_scan_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Scan Configuration'),
            'res_model': 'fs.guardian.snapshot.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_baseline_id': self.id},
        }

    def action_view_changes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Configuration Changes'),
            'res_model': 'fs.guardian.change',
            'view_mode': 'list,form',
            'domain': [('baseline_id', '=', self.id)],
            'context': {'default_baseline_id': self.id},
        }

    @api.model
    def get_dashboard_data(self):
        company = self.env.company
        Baseline = self.env['fs.guardian.baseline']
        Change = self.env['fs.guardian.change']
        Snapshot = self.env['fs.guardian.snapshot']

        active_baselines = Baseline.search([('company_id', '=', company.id), ('state', '=', 'active')], order='id desc')
        open_domain = [('company_id', '=', company.id), ('status', 'not in', ['approved', 'expected'])]
        all_domain = [('company_id', '=', company.id)]

        def count(extra=None):
            return Change.search_count(open_domain + (extra or []))

        category_labels = dict(Change._fields['category'].selection)
        risk_labels = dict(Change._fields['risk_level'].selection)
        status_labels = dict(Change._fields['status'].selection)
        operation_labels = dict(Change._fields['operation'].selection)

        categories = []
        for key, label in Change._fields['category'].selection:
            value = count([('category', '=', key)])
            if value:
                categories.append({'key': key, 'label': label, 'value': value})
        categories.sort(key=lambda row: row['value'], reverse=True)

        risks = [{
            'key': key, 'label': label,
            'value': Change.search_count(all_domain + [('risk_level', '=', key)]),
            'open_value': count([('risk_level', '=', key)]),
        } for key, label in Change._fields['risk_level'].selection]

        statuses = [{
            'key': key, 'label': label,
            'value': Change.search_count(all_domain + [('status', '=', key)]),
        } for key, label in Change._fields['status'].selection]

        recent_changes = []
        for change in Change.search(all_domain, order='detected_at desc, id desc', limit=8):
            recent_changes.append({
                'id': change.id, 'name': change.name,
                'category': change.category, 'category_label': category_labels.get(change.category, change.category),
                'operation': change.operation, 'operation_label': operation_labels.get(change.operation, change.operation),
                'risk_level': change.risk_level, 'risk_label': risk_labels.get(change.risk_level, change.risk_level),
                'status': change.status, 'status_label': status_labels.get(change.status, change.status),
                'detected_at': fields.Datetime.to_string(change.detected_at),
                'record_label': change.record_label or change.record_key,
            })

        baselines = []
        for baseline in active_baselines[:5]:
            baselines.append({
                'id': baseline.id, 'name': baseline.name, 'state': baseline.state,
                'health_score': baseline.health_score, 'critical_count': baseline.critical_count,
                'high_count': baseline.high_count, 'medium_count': baseline.medium_count,
                'change_count': baseline.change_count,
                'last_scan_at': fields.Datetime.to_string(baseline.last_scan_at) if baseline.last_scan_at else False,
            })

        latest_snapshot = Snapshot.search([('company_id', '=', company.id)], order='captured_at desc, id desc', limit=1)
        today = fields.Date.context_today(self)
        trend = []
        for offset in range(6, -1, -1):
            day = fields.Date.subtract(today, days=offset)
            start = fields.Datetime.to_datetime(day)
            end = fields.Datetime.to_datetime(fields.Date.add(day, days=1))
            trend.append({
                'date': fields.Date.to_string(day),
                'value': Change.search_count(all_domain + [('detected_at', '>=', fields.Datetime.to_string(start)), ('detected_at', '<', fields.Datetime.to_string(end))]),
                'critical': Change.search_count(all_domain + [('detected_at', '>=', fields.Datetime.to_string(start)), ('detected_at', '<', fields.Datetime.to_string(end)), ('risk_level', '=', 'critical')]),
            })

        critical = count([('risk_level', '=', 'critical')])
        high = count([('risk_level', '=', 'high')])
        medium = count([('risk_level', '=', 'medium')])
        return {
            'company': {'id': company.id, 'name': company.display_name},
            'kpis': {
                'health_score': max(0, 100 - critical * 20 - high * 8 - medium * 2),
                'active_baselines': len(active_baselines), 'open_changes': count(),
                'critical': critical, 'high': high, 'medium': medium,
                'total_changes': Change.search_count(all_domain),
            },
            'categories': categories, 'risks': risks, 'statuses': statuses,
            'recent_changes': recent_changes, 'baselines': baselines, 'trend': trend,
            'latest_snapshot': {
                'id': latest_snapshot.id if latest_snapshot else False,
                'name': latest_snapshot.name if latest_snapshot else False,
                'state': latest_snapshot.state if latest_snapshot else False,
                'captured_at': fields.Datetime.to_string(latest_snapshot.captured_at) if latest_snapshot else False,
                'item_count': latest_snapshot.item_count if latest_snapshot else 0,
            },
        }

