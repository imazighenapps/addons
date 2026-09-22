from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestTreatmentPlan(models.Model):
    _name = 'pest.treatment.plan'
    _description = 'Pest Treatment Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'site_id, start_date desc, id desc'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.treatment.plan'),
        readonly=True,
        copy=False,
    )
    site_id = fields.Many2one(
        'pest.site',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    contract_id = fields.Many2one(
        'pest.contract',
        ondelete='restrict',
        tracking=True,
        index=True,
    )
    contract_site_line_id = fields.Many2one(
        'pest.contract.site',
        ondelete='restrict',
        tracking=True,
        index=True,
    )
    company_id = fields.Many2one(
        related='site_id.company_id',
        store=True,
        index=True,
    )

    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date()
    active = fields.Boolean(default=True, tracking=True)

    frequency_type = fields.Selection(
        [
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
        ],
        default=lambda self: self.env.company.pestops_default_frequency_type or 'weeks',
        required=True,
    )
    frequency_number = fields.Integer(default=lambda self: self.env.company.pestops_default_frequency_number or 2, required=True)
    visit_duration_minutes = fields.Integer(
        string='Visit Duration',
        default=lambda self: self.env.company.pestops_default_visit_duration_minutes or 60,
        required=True,
        help='Expected duration of each operational visit in minutes.',
    )

    visit_horizon_days = fields.Integer(
        string='Generation Horizon',
        default=lambda self: self.env.company.pestops_default_plan_horizon_days or 60,
        required=True,
        help='Cron generates visits up to this many days ahead.',
    )

    responsible_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
    )
    technician_id = fields.Many2one(
        'res.users',
        string='Default Technician',
    )
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'High')],
        default='0',
    )

    line_ids = fields.One2many(
        'pest.treatment.plan.line',
        'plan_id',
        copy=True,
    )
    visit_ids = fields.One2many('pest.visit', 'plan_id')

    next_visit_date = fields.Datetime(compute='_compute_next_visit_date', store=True)
    visit_count = fields.Integer(compute='_compute_counts')
    generated_visit_count = fields.Integer(compute='_compute_counts')

    @api.depends('visit_ids.scheduled_start', 'visit_ids.state')
    def _compute_next_visit_date(self):
        for plan in self:
            visits = plan.visit_ids.filtered(
                lambda v: v.state in ('draft', 'scheduled') and v.scheduled_start
            )
            plan.next_visit_date = min(visits.mapped('scheduled_start'), default=False)

    def _compute_counts(self):
        for plan in self:
            plan.visit_count = len(plan.visit_ids)
            plan.generated_visit_count = len(plan.visit_ids.filtered(
                lambda v: v.generated_from_plan
            ))

    @api.constrains('frequency_number', 'visit_duration_minutes', 'visit_horizon_days')
    def _check_positive_settings(self):
        for plan in self:
            if plan.frequency_number <= 0:
                raise ValidationError(_('Frequency must be greater than zero.'))
            if plan.visit_duration_minutes <= 0:
                raise ValidationError(_('Visit duration must be greater than zero.'))
            if plan.visit_horizon_days <= 0:
                raise ValidationError(_('Generation horizon must be greater than zero.'))

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for plan in self:
            if plan.end_date and plan.end_date < plan.start_date:
                raise ValidationError(_('End date must be on or after the start date.'))

    def _frequency_delta(self):
        self.ensure_one()
        if self.frequency_type == 'days':
            return relativedelta(days=self.frequency_number)
        if self.frequency_type == 'weeks':
            return relativedelta(weeks=self.frequency_number)
        return relativedelta(months=self.frequency_number)

    def _first_visit_datetime(self):
        self.ensure_one()
        tz = self.env.user.tz or 'UTC'
        # Keep V1 deterministic and timezone-safe: midnight in the server user's date
        # is used as the initial scheduled date; later UI scheduling can refine the time.
        return fields.Datetime.to_datetime(self.start_date)

    def _next_generated_start(self, last_start):
        self.ensure_one()
        return last_start + self._frequency_delta()

    def _prepare_visit_vals(self, scheduled_start):
        self.ensure_one()
        duration = self.visit_duration_minutes
        scheduled_end = scheduled_start + timedelta(minutes=duration)
        return {
            'site_id': self.site_id.id,
            'plan_id': self.id,
            'technician_id': self.technician_id.id if self.technician_id else False,
            'scheduled_start': scheduled_start,
            'scheduled_end': scheduled_end,
            'priority': self.priority,
            'state': 'scheduled',
            'generated_from_plan': True,
            'origin_generation_date': fields.Datetime.now(),
        }

    def action_generate_visits(self):
        Visit = self.env['pest.visit']
        now = fields.Datetime.now()

        for plan in self:
            if not plan.active:
                continue

            start = plan._first_visit_datetime()
            existing = Visit.search(
                [('plan_id', '=', plan.id)],
                order='scheduled_start asc, id asc',
            )

            if existing:
                cursor = max(existing.mapped('scheduled_start'))
            else:
                cursor = start

            horizon = now + timedelta(days=plan.visit_horizon_days)
            max_end = (
                fields.Datetime.to_datetime(plan.end_date) + timedelta(days=1)
                if plan.end_date
                else False
            )
            effective_horizon = min(horizon, max_end) if max_end else horizon

            created = 0
            # First visit can be generated at the plan start.
            if not existing and cursor <= effective_horizon:
                Visit.create(plan._prepare_visit_vals(cursor))
                created += 1

            safety = 0
            while safety < 500:
                safety += 1
                next_start = plan._next_generated_start(cursor)
                if next_start > effective_horizon:
                    break
                vals = plan._prepare_visit_vals(next_start)
                Visit.create(vals)
                cursor = next_start
                created += 1

        return True

    def action_generate_now(self):
        self.action_generate_visits()
        return True


class PestTreatmentPlanLine(models.Model):
    _name = 'pest.treatment.plan.line'
    _description = 'Pest Treatment Plan Line'

    plan_id = fields.Many2one(
        'pest.treatment.plan',
        required=True,
        ondelete='cascade',
    )
    zone_id = fields.Many2one(
        'pest.zone',
        required=True,
        ondelete='restrict',
        domain="[('site_id', '=', parent.site_id)]",
    )
    pest_id = fields.Many2one('pest.type', ondelete='restrict')
    method_id = fields.Many2one('pest.treatment.method', ondelete='restrict')
    control_point_ids = fields.Many2many(
        'pest.control.point',
        relation='pest_plan_line_control_point_rel',
        column1='plan_line_id',
        column2='control_point_id',
    )
    instructions = fields.Html()
    duration_minutes = fields.Integer(default=30)
    active = fields.Boolean(default=True)
