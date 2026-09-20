from datetime import timedelta

from odoo import api, fields, models


class SmartOperationsBaselineEngine(models.AbstractModel):
    _name = 'smart.operations.baseline.engine'
    _description = 'Process Baseline Engine'

    @api.model
    def refresh(self, processes=None):
        analyzer = self.env['smart.operations.process.analyzer']
        processes = processes or self.env['smart.operations.process'].search([('active', '=', True)])
        now = fields.Datetime.now()
        created = self.env['smart.operations.baseline']

        for process in processes:
            if not all((process.source_model, process.start_field, process.end_field)):
                continue

            baseline_start = now - timedelta(days=process.baseline_window_days)
            baseline_end = now - timedelta(days=process.current_window_days)
            baseline = analyzer.analyze_simple_delay_process(
                process,
                start_date=baseline_start,
                end_date=baseline_end,
            )
            current = analyzer.analyze_current_window(process)
            if not baseline or baseline['count'] < process.minimum_samples:
                continue
            if not current:
                continue

            values = {
                'process_id': process.id,
                'period_start': baseline_start,
                'period_end': baseline_end,
                'sample_count': baseline['count'],
                'average_days': baseline['average'],
                'median_days': baseline['median'],
                'p75_days': baseline['p75'],
                'p90_days': baseline['p90'],
                'minimum_days': baseline['min'],
                'maximum_days': baseline['max'],
                'current_days': current['average'],
            }
            existing = self.env['smart.operations.baseline'].search([
                ('process_id', '=', process.id),
                ('period_start', '=', baseline_start),
                ('period_end', '=', baseline_end),
            ], limit=1)
            if existing:
                existing.write(values)
                created |= existing
            else:
                created |= self.env['smart.operations.baseline'].create(values)
        return created

    @api.model
    def _cron_refresh_baselines(self):
        self.refresh()
        return True
