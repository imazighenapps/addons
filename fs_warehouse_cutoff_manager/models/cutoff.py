from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


WEEKDAYS = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]


class WarehouseCutoffRule(models.Model):
    _name = 'fs.warehouse.cutoff.rule'
    _description = 'Warehouse Cut-off Rule'
    _check_company_auto = True
    _order = 'warehouse_id, weekday, cutoff_hour'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade',
        index=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        required=True,
        check_company=True,
        index=True,
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        required=True,
        check_company=True,
        index=True,
    )
    carrier_id = fields.Many2one(
        'delivery.carrier',
        check_company=True,
        help='Optional carrier restriction. Leave empty to apply to every carrier.',
    )
    weekday = fields.Selection(
        [(str(i), name) for i, name in enumerate(WEEKDAYS)],
        required=True,
    )
    cutoff_hour = fields.Float(default=16.0, required=True)
    warning_minutes = fields.Integer(default=60, required=True)
    timezone = fields.Selection(
        selection=lambda self: [(zone, zone) for zone in pytz.common_timezones],
        default=lambda self: self.env.user.tz or 'UTC',
        required=True,
    )
    allow_next_day = fields.Boolean(
        string='Cut-off on Following Day',
        help='Apply this rule to transfers scheduled on the previous local weekday.',
    )
    active = fields.Boolean(default=True)
    notification_mode = fields.Selection(
        [('none', 'No notification'), ('activity', 'Create activity')],
        default='activity',
        required=True,
    )

    @api.constrains('cutoff_hour')
    def _check_hour(self):
        for rec in self:
            if not 0 <= rec.cutoff_hour < 24:
                raise ValidationError(_('Cut-off hour must be between 0 and 24.'))

    @api.constrains('warning_minutes')
    def _check_warning_minutes(self):
        for rec in self:
            if rec.warning_minutes < 0:
                raise ValidationError(_('Warning time cannot be negative.'))

    @api.constrains('picking_type_id', 'warehouse_id', 'company_id', 'carrier_id')
    def _check_picking_type_warehouse(self):
        for rec in self:
            if rec.warehouse_id.company_id != rec.company_id:
                raise ValidationError(_('The warehouse must belong to the selected company.'))
            if rec.picking_type_id.warehouse_id != rec.warehouse_id:
                raise ValidationError(_('The operation type must belong to the selected warehouse.'))
            if rec.carrier_id and rec.carrier_id.company_id and rec.carrier_id.company_id != rec.company_id:
                raise ValidationError(_('The carrier must belong to the selected company.'))

    @api.constrains('warehouse_id', 'picking_type_id', 'weekday', 'carrier_id')
    def _check_duplicate_rule(self):
        for record in self:
            domain = [
                ('id', '!=', record.id),
                ('warehouse_id', '=', record.warehouse_id.id),
                ('picking_type_id', '=', record.picking_type_id.id),
                ('weekday', '=', record.weekday),
                ('carrier_id', '=', record.carrier_id.id if record.carrier_id else False),
            ]
            if self.search_count(domain):
                raise ValidationError(_(
                    'Only one cut-off rule can exist for this warehouse, operation, weekday and carrier.'
                ))


class WarehouseCutoffMonitor(models.Model):
    _name = 'fs.warehouse.cutoff.monitor'
    _description = 'Warehouse Cut-off Monitor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _order = 'status desc, minutes_to_cutoff asc'

    picking_id = fields.Many2one('stock.picking', required=True, index=True, ondelete='cascade')
    rule_id = fields.Many2one(
        'fs.warehouse.cutoff.rule',
        required=True,
        ondelete='cascade',
        check_company=True,
    )
    company_id = fields.Many2one(related='picking_id.company_id', store=True, index=True)
    warehouse_id = fields.Many2one(related='rule_id.warehouse_id', store=True)
    picking_type_id = fields.Many2one(related='picking_id.picking_type_id', store=True)
    scheduled_date = fields.Datetime(related='picking_id.scheduled_date', store=True, index=True)
    cutoff_datetime = fields.Datetime(readonly=True, index=True)
    minutes_to_cutoff = fields.Float(readonly=True)
    ready = fields.Boolean(readonly=True)
    status = fields.Selection([
        ('ship_today', 'Ship Today'),
        ('at_risk', 'At Risk'),
        ('missed_cutoff', 'Missed Cutoff'),
        ('completed', 'Completed'),
    ], required=True, index=True)
    reason = fields.Char(readonly=True)
    last_checked_at = fields.Datetime(readonly=True)

    _picking_rule_unique = models.Constraint(
        'unique (picking_id,rule_id)',
        'A picking can have one monitoring record per rule.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_cutoff_internal'):
            raise ValidationError(_('Warehouse cut-off monitor rows are generated by the monitoring engine.'))
        return super().create(vals_list)

    def write(self, vals):
        if vals and not self.env.context.get('fs_cutoff_internal'):
            raise ValidationError(_('Warehouse cut-off monitor rows are system-generated and cannot be edited manually.'))
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get('fs_cutoff_internal'):
            raise ValidationError(_('Warehouse cut-off monitor rows are system-generated and cannot be deleted manually.'))
        return super().unlink()


    def action_open_picking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.picking_id.id,
            'name': _('Transfer'),
        }

    def action_refresh(self):
        self.ensure_one()
        self.refresh(self.picking_id)
        return True

    @api.model
    def _compute_cutoff(self, picking, rule):
        """Return the cutoff instant in naive UTC, respecting the configured timezone."""
        if not picking.scheduled_date:
            return False
        tz = pytz.timezone(rule.timezone or 'UTC')
        local_sched = pytz.UTC.localize(picking.scheduled_date).astimezone(tz)
        scheduled_weekday = local_sched.weekday()
        rule_weekday = int(rule.weekday)
        delta = (rule_weekday - scheduled_weekday) % 7
        if delta and not (delta == 1 and rule.allow_next_day):
            return False

        target_date = local_sched.date() + timedelta(days=delta)
        hour = int(rule.cutoff_hour)
        minute = min(int(round((rule.cutoff_hour - hour) * 60)), 59)
        local_cutoff = tz.localize(datetime.combine(target_date, time(hour, minute)))
        return local_cutoff.astimezone(pytz.UTC).replace(tzinfo=None)

    @api.model
    def _rule_applies(self, picking, rule):
        if not picking.scheduled_date:
            return False
        tz = pytz.timezone(rule.timezone or 'UTC')
        local_sched = pytz.UTC.localize(picking.scheduled_date).astimezone(tz)
        scheduled_weekday = local_sched.weekday()
        rule_weekday = int(rule.weekday)
        delta = (rule_weekday - scheduled_weekday) % 7
        return delta == 0 or (delta == 1 and rule.allow_next_day)

    @api.model
    def _evaluate(self, picking, rule, cutoff, now):
        if picking.state == 'done':
            return {
                'status': 'completed',
                'reason': _('Transfer completed.'),
                'ready': True,
                'minutes_to_cutoff': 0.0,
            }

        minutes = (cutoff - now).total_seconds() / 60.0
        ready = picking.state == 'assigned'
        if minutes < 0:
            status = 'missed_cutoff'
            reason = _('The shipping cut-off has passed before the transfer was completed.')
        elif not ready:
            status = 'at_risk'
            reason = _(
                'The transfer is not ready for shipping before the configured cut-off.'
            )
        elif minutes <= rule.warning_minutes:
            status = 'at_risk'
            reason = _('The transfer is ready but approaching its shipping cut-off.')
        else:
            status = 'ship_today'
            reason = _('The transfer is ready and remains before its shipping cut-off.')

        return {
            'status': status,
            'reason': reason,
            'ready': ready,
            'minutes_to_cutoff': minutes,
        }

    @api.model
    def refresh(self, pickings=None):
        rules = self.env['fs.warehouse.cutoff.rule'].search([('active', '=', True)])
        if pickings is None or not pickings:
            pickings = self.env['stock.picking'].browse()
        else:
            pickings = pickings.filtered(lambda p: p.state != 'cancel')

        if not pickings:
            return True

        existing = self.search([('picking_id', 'in', pickings.ids)])
        by_key = {(rec.picking_id.id, rec.rule_id.id): rec for rec in existing}
        now = fields.Datetime.now()
        keep = set()

        for picking in pickings:
            if picking.picking_type_id.code != 'outgoing' or not picking.scheduled_date:
                continue
            candidates = rules.filtered(lambda rule: (
                rule.company_id == picking.company_id
                and rule.warehouse_id == picking.picking_type_id.warehouse_id
                and rule.picking_type_id == picking.picking_type_id
                and (not rule.carrier_id or rule.carrier_id == picking.carrier_id)
                and self._rule_applies(picking, rule)
            ))
            for rule in candidates:
                cutoff = self._compute_cutoff(picking, rule)
                if not cutoff:
                    continue
                values = self._evaluate(picking, rule, cutoff, now)
                values.update({
                    'picking_id': picking.id,
                    'rule_id': rule.id,
                    'cutoff_datetime': cutoff,
                    'last_checked_at': now,
                })
                key = (picking.id, rule.id)
                keep.add(key)
                rec = by_key.get(key)
                previous_status = rec.status if rec else False
                if rec:
                    rec.with_context(fs_cutoff_internal=True).write(values)
                else:
                    rec = self.with_context(fs_cutoff_internal=True).create(values)
                if (
                    rule.notification_mode == 'activity'
                    and previous_status != rec.status
                    and rec.status in ('at_risk', 'missed_cutoff')
                    and picking.user_id
                ):
                    rec.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=picking.user_id.id,
                        summary=_(
                            'Warehouse cut-off status: %(status)s',
                            status=rec.status.replace('_', ' ').title(),
                        ),
                        note=rec.reason,
                    )

        for key, rec in by_key.items():
            if key in keep or key[0] not in pickings.ids:
                continue
            rec.with_context(fs_cutoff_internal=True).unlink()
        self.search([('picking_id.state', '=', 'cancel')]).with_context(fs_cutoff_internal=True).unlink()
        return True

    @api.model
    def cron_refresh(self, batch_size=500):
        """Refresh all outgoing transfers in bounded batches plus outstanding completions."""
        Picking = self.env['stock.picking']
        last_id = 0
        while True:
            pickings = Picking.search([
                ('id', '>', last_id),
                ('state', 'not in', ('cancel',)),
                ('picking_type_id.code', '=', 'outgoing'),
            ], order='id', limit=batch_size)
            if not pickings:
                break
            self.refresh(pickings)
            last_id = pickings[-1].id

        monitored_done = self.search([('status', '!=', 'completed')]).mapped('picking_id').filtered(
            lambda picking: picking.state == 'done'
        )
        if monitored_done:
            self.refresh(monitored_done)
        return True
