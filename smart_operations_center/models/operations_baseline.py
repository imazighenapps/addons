from odoo import api, fields, models


class SmartOperationsBaseline(models.Model):
    _name = 'smart.operations.baseline'
    _description = 'Process Performance Baseline'
    _order = 'period_end desc, id desc'

    _sql_constraints = [
        (
            'baseline_period_unique',
            'unique(process_id, period_start, period_end)',
            'A process can only have one baseline for the same measurement period.',
        ),
    ]

    process_id = fields.Many2one('smart.operations.process', required=True, ondelete='cascade')
    period_start = fields.Datetime(required=True)
    period_end = fields.Datetime(required=True)
    sample_count = fields.Integer(default=0)
    average_days = fields.Float()
    median_days = fields.Float()
    p75_days = fields.Float()
    p90_days = fields.Float()
    minimum_days = fields.Float()
    maximum_days = fields.Float()
    current_days = fields.Float()
    deviation_percent = fields.Float(compute='_compute_deviation', store=True)
    health = fields.Selection([('healthy', 'Healthy'), ('watch', 'Watch'), ('critical', 'Critical')], compute='_compute_health', store=True)

    @api.depends('average_days', 'current_days')
    def _compute_deviation(self):
        for record in self:
            record.deviation_percent = ((record.current_days - record.average_days) / record.average_days * 100.0) if record.average_days else 0.0

    @api.depends('deviation_percent')
    def _compute_health(self):
        for record in self:
            if record.deviation_percent >= 50:
                record.health = 'critical'
            elif record.deviation_percent >= 20:
                record.health = 'watch'
            else:
                record.health = 'healthy'
