from datetime import datetime, timedelta
from statistics import median

from odoo import api, fields, models


class SmartOperationsProcessAnalyzer(models.AbstractModel):
    _name = 'smart.operations.process.analyzer'
    _description = 'Process Performance Analyzer'

    @staticmethod
    def _percentile(values, percentile):
        if not values:
            return 0.0
        if len(values) == 1:
            return values[0]
        position = (len(values) - 1) * percentile
        lower = int(position)
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        return values[lower] + (values[upper] - values[lower]) * fraction

    @staticmethod
    def _to_datetime(value):
        if not value:
            return False
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return fields.Datetime.to_datetime(value)
        return datetime.combine(value, datetime.min.time())

    @api.model
    def _measure_records(self, records, start_field, end_field):
        durations = []
        for record in records:
            start = self._to_datetime(record[start_field])
            end = self._to_datetime(record[end_field])
            if not start or not end or end < start:
                continue
            durations.append((end - start).total_seconds() / 86400.0)
        durations.sort()
        if not durations:
            return False
        return {
            'count': len(durations),
            'average': sum(durations) / len(durations),
            'median': median(durations),
            'p75': self._percentile(durations, 0.75),
            'p90': self._percentile(durations, 0.90),
            'min': durations[0],
            'max': durations[-1],
        }

    @api.model
    def analyze_simple_delay_process(self, process, source_model=None, start_field=None, end_field=None, days=90, start_date=None, end_date=None):
        source_model = source_model or process.source_model
        start_field = start_field or process.start_field
        end_field = end_field or process.end_field
        if not all((source_model, start_field, end_field)):
            return False

        model = self.env.get(source_model)
        if not model or start_field not in model._fields or end_field not in model._fields:
            return False

        end_date = end_date or fields.Datetime.now()
        start_date = start_date or (end_date - timedelta(days=days))
        domain = [
            (start_field, '>=', fields.Datetime.to_string(start_date)),
            (start_field, '<', fields.Datetime.to_string(end_date)),
            (end_field, '!=', False),
            (end_field, '<=', fields.Datetime.to_string(end_date)),
        ]
        records = model.search(domain, order=f'{start_field} asc', limit=5000)
        return self._measure_records(records, start_field, end_field)

    @api.model
    def analyze_current_window(self, process):
        if not process.source_model:
            return False
        model = self.env.get(process.source_model)
        if not model or process.start_field not in model._fields or process.end_field not in model._fields:
            return False
        since = fields.Datetime.now() - timedelta(days=process.current_window_days)
        records = model.search([
            (process.start_field, '>=', fields.Datetime.to_string(since)),
            (process.end_field, '!=', False),
            (process.end_field, '<=', fields.Datetime.to_string(fields.Datetime.now())),
        ], order=f'{process.start_field} asc', limit=5000)
        return self._measure_records(records, process.start_field, process.end_field)
