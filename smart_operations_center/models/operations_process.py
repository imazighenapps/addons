from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SmartOperationsProcess(models.Model):
    _name = 'smart.operations.process'
    _description = 'Operational Process'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    application = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('stock', 'Inventory'),
        ('mrp', 'Manufacturing'),
        ('account', 'Accounting'),
        ('crm', 'CRM'),
        ('cross', 'Cross-Application'),
    ], required=True, default='cross')
    description = fields.Text()

    source_model = fields.Char(
        string='Source Model',
        help='Technical model containing the process completion records, for example purchase.order.',
    )
    start_field = fields.Char(
        string='Start Datetime Field',
        help='Technical field containing the process start date/time.',
    )
    end_field = fields.Char(
        string='End Datetime Field',
        help='Technical field containing the process completion date/time.',
    )
    baseline_window_days = fields.Integer(default=90, required=True)
    current_window_days = fields.Integer(default=14, required=True)
    minimum_samples = fields.Integer(default=5, required=True)
    baseline_ids = fields.One2many(
        'smart.operations.baseline', 'process_id', string='Baselines'
    )

    @api.constrains('baseline_window_days', 'current_window_days', 'minimum_samples')
    def _check_windows(self):
        for process in self:
            if process.baseline_window_days < 7:
                raise ValidationError('The baseline window must be at least 7 days.')
            if process.current_window_days < 1:
                raise ValidationError('The current window must be at least 1 day.')
            if process.minimum_samples < 1:
                raise ValidationError('Minimum samples must be at least 1.')

    @api.constrains('source_model', 'start_field', 'end_field')
    def _check_measurement_configuration(self):
        for process in self:
            if not any((process.source_model, process.start_field, process.end_field)):
                continue
            if not all((process.source_model, process.start_field, process.end_field)):
                raise ValidationError(
                    'Source Model, Start Datetime Field and End Datetime Field must be configured together.'
                )
            model = self.env.get(process.source_model)
            if not model:
                continue
            missing = [
                field_name
                for field_name in (process.start_field, process.end_field)
                if field_name not in model._fields
            ]
            if missing:
                raise ValidationError(
                    'The following fields do not exist on %s: %s'
                    % (process.source_model, ', '.join(missing))
                )
