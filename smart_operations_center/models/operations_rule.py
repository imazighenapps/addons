from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SmartOperationsRule(models.Model):
    _name = 'smart.operations.rule'
    _description = 'Operational Monitoring Rule'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    model_id = fields.Many2one('ir.model', required=True, ondelete='cascade')
    domain = fields.Char(default='[]', required=True, help='Restricted Odoo domain. Date tokens: today, today-Nd, now, now-NNh.')
    rule_issue_type = fields.Selection([
        ('delay', 'Delay'),
        ('stagnation', 'Stagnation'),
        ('deadline_risk', 'Deadline Risk'),
        ('dependency', 'Dependency'),
        ('missing_action', 'Missing Action'),
        ('business_risk', 'Business Risk'),
    ], default='delay', required=True)
    severity = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical'),
    ], default='medium', required=True)
    risk_weight = fields.Float(default=5.0)
    responsible_id = fields.Many2one('res.users', ondelete='set null')
    escalation_policy_id = fields.Many2one('smart.operations.escalation', ondelete='set null')
    action_create_activity = fields.Boolean(default=True)
    action_email = fields.Boolean(default=False)
    activity_due_hours = fields.Float(default=24.0)
    date_field = fields.Char(help='Optional technical date/datetime field used to calculate delay.')
    max_records_per_run = fields.Integer(default=200)
    description = fields.Text()

    @api.constrains('max_records_per_run', 'activity_due_hours', 'risk_weight')
    def _check_values(self):
        for rule in self:
            if rule.max_records_per_run < 1 or rule.max_records_per_run > 5000:
                raise ValidationError(_('Maximum records per run must be between 1 and 5000.'))
            if rule.activity_due_hours < 0:
                raise ValidationError(_('Activity due time cannot be negative.'))
            if not 0 <= rule.risk_weight <= 10:
                raise ValidationError(_('Risk weight must be between 0 and 10.'))
            if rule.date_field and rule.model_id and rule.date_field not in self.env[rule.model_id.model]._fields:
                raise ValidationError(_('Date field %s does not exist on %s.') % (rule.date_field, rule.model_id.model))

    @api.constrains('domain', 'model_id')
    def _check_domain(self):
        detector = self.env['smart.operations.issue.detector']
        for rule in self:
            domain = detector._safe_domain(rule.domain)
            model = self.env.get(rule.model_id.model)
            if model:
                try:
                    model.search(domain, limit=1)
                except Exception as exc:
                    raise ValidationError(_('The monitoring domain is not valid for %s: %s') % (rule.model_id.model, exc)) from exc

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            self.description = _('Monitor %s for operational risk.') % self.model_id.name
