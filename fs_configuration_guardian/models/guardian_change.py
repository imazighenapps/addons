import hashlib
import json

from odoo import api, fields, models, _


class GuardianChange(models.Model):
    _name = 'fs.guardian.change'
    _description = 'Detected Configuration Change'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'detected_at desc, id desc'

    name = fields.Char(required=True, tracking=True)
    baseline_id = fields.Many2one('fs.guardian.baseline', required=True, index=True, ondelete='cascade')
    company_id = fields.Many2one(related='baseline_id.company_id', store=True, index=True)
    category = fields.Selection([
        ('security', 'Security'), ('automation', 'Automation'), ('studio', 'Studio'),
        ('accounting', 'Accounting'), ('inventory', 'Inventory'), ('sales', 'Sales'),
        ('technical', 'Technical'),
    ], required=True, index=True)
    operation = fields.Selection([('added', 'Added'), ('modified', 'Modified'), ('removed', 'Removed')], required=True)
    model_name = fields.Char(required=True, index=True)
    record_key = fields.Char(required=True)
    record_label = fields.Char()
    external_id = fields.Char()
    detected_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    detected_by = fields.Many2one('res.users', default=lambda self: self.env.user, required=True)
    before_data = fields.Json(default=dict)
    after_data = fields.Json(default=dict)
    risk_level = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')
    ], required=True, default='low', index=True, tracking=True)
    risk_reason = fields.Text()
    status = fields.Selection([
        ('unknown', 'Unknown'), ('expected', 'Expected'), ('approved', 'Approved'), ('rejected', 'Rejected')
    ], default='unknown', required=True, tracking=True, index=True)
    reviewer_id = fields.Many2one('res.users')
    reviewed_at = fields.Datetime()
    review_note = fields.Text()
    fingerprint = fields.Char(required=True, index=True, copy=False)

    _sql_constraints = [
        ('fingerprint_uniq', 'unique(fingerprint)', 'This configuration change has already been detected for this baseline.'),
    ]

    @staticmethod
    def _fingerprint(baseline, item, before, after, operation):
        payload = {
            'baseline': baseline.id,
            'category': item.get('category'),
            'model': item.get('model'),
            'key': item.get('key'),
            'operation': operation,
            'before': before or {},
            'after': after or {},
        }
        raw = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    def _review(self, status):
        self.write({'status': status, 'reviewer_id': self.env.user.id, 'reviewed_at': fields.Datetime.now()})

    def action_mark_expected(self):
        self._review('expected')

    def action_mark_approved(self):
        self._review('approved')

    def action_mark_rejected(self):
        self._review('rejected')

    def action_reset_review(self):
        self.write({'status': 'unknown', 'reviewer_id': False, 'reviewed_at': False, 'review_note': False})

    @api.model
    def create_change(self, baseline, item, before, after, operation, risk):
        fingerprint = self._fingerprint(baseline, item, before, after, operation)
        existing = self.search([('fingerprint', '=', fingerprint)], limit=1)
        if existing:
            return existing
        before_values = before or {}
        after_values = after or {}
        label = item.get('label') or item.get('key')
        return self.create({
            'name': _('%s: %s') % (item.get('category', '').title(), label),
            'baseline_id': baseline.id,
            'category': item['category'],
            'operation': operation,
            'model_name': item['model'],
            'record_key': item['key'],
            'record_label': label,
            'external_id': item.get('external_id'),
            'before_data': before_values,
            'after_data': after_values,
            'risk_level': risk['level'],
            'risk_reason': risk['reason'],
            'fingerprint': fingerprint,
        })
