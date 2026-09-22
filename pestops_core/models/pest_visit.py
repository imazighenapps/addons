from datetime import timedelta
import math

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestVisit(models.Model):
    _name = 'pest.visit'
    _description = 'Pest Control Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_start asc, id asc'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.visit'),
        readonly=True,
        copy=False,
    )
    site_id = fields.Many2one(
        'pest.site',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    company_id = fields.Many2one(
        related='site_id.company_id',
        store=True,
        index=True,
    )
    plan_id = fields.Many2one(
        'pest.treatment.plan',
        ondelete='restrict',
        tracking=True,
    )
    contract_id = fields.Many2one(
        'pest.contract',
        related='plan_id.contract_id',
        store=True,
        index=True,
    )
    technician_id = fields.Many2one(
        'res.users',
        string='Technician',
        tracking=True,
    )
    task_id = fields.Many2one(
        'project.task',
        string='Project Task',
        readonly=True,
        copy=False,
    )

    scheduled_start = fields.Datetime(tracking=True)
    scheduled_end = fields.Datetime(tracking=True)
    actual_start = fields.Datetime()
    actual_end = fields.Datetime()

    generated_from_plan = fields.Boolean(
        default=False,
        readonly=True,
        copy=False,
    )
    origin_generation_date = fields.Datetime(
        readonly=True,
        copy=False,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )

    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'High')],
        default='0',
    )

    inspection_ids = fields.One2many('pest.inspection', 'visit_id')
    treatment_ids = fields.One2many('pest.treatment', 'visit_id')
    reservice_ids = fields.One2many('pest.reservice', 'origin_visit_id')
    anomaly_ids = fields.One2many('pest.anomaly', 'visit_id', string='Anomalies')

    inspection_required = fields.Boolean(
        default=lambda self: self.env.company.pestops_require_inspection_before_close,
        tracking=True,
    )
    treatment_required = fields.Boolean(
        default=lambda self: self.env.company.pestops_require_treatment_before_close,
        tracking=True,
    )
    completion_outcome = fields.Selection([
        ('normal', 'Completed'),
        ('follow_up', 'Follow-up Required'),
        ('critical', 'Critical Findings'),
    ], default='normal', tracking=True)
    completion_summary = fields.Text()

    anomaly_count = fields.Integer(compute='_compute_counts')
    open_anomaly_count = fields.Integer(compute='_compute_counts')

    inspection_count = fields.Integer(compute='_compute_counts')
    treatment_count = fields.Integer(compute='_compute_counts')
    reservice_count = fields.Integer(compute='_compute_counts')

    notes = fields.Html()
    customer_feedback = fields.Text()

    mobile_checkin_used = fields.Boolean(default=False, readonly=True, copy=False, tracking=True)
    checkin_latitude = fields.Float(digits=(10, 7), readonly=True, copy=False)
    checkin_longitude = fields.Float(digits=(10, 7), readonly=True, copy=False)
    checkin_accuracy = fields.Float(string='Check-in Accuracy (m)', readonly=True, copy=False)
    checkin_at = fields.Datetime(readonly=True, copy=False)
    checkout_latitude = fields.Float(digits=(10, 7), readonly=True, copy=False)
    checkout_longitude = fields.Float(digits=(10, 7), readonly=True, copy=False)
    checkout_accuracy = fields.Float(string='Check-out Accuracy (m)', readonly=True, copy=False)
    checkout_at = fields.Datetime(readonly=True, copy=False)
    customer_signature = fields.Binary(string='Customer Signature', attachment=True, copy=False)
    customer_signature_name = fields.Char(string='Signed By', copy=False)
    customer_signature_date = fields.Datetime(string='Signature Date', readonly=True, copy=False)
    customer_signature_note = fields.Text(string='Customer Signature Note', copy=False)

    mobile_duration_minutes = fields.Float(
        string='Field Duration (min)',
        compute='_compute_mobile_duration',
    )

    @api.depends('actual_start', 'actual_end')
    def _compute_mobile_duration(self):
        for visit in self:
            if visit.actual_start and visit.actual_end:
                visit.mobile_duration_minutes = max(
                    (visit.actual_end - visit.actual_start).total_seconds() / 60.0, 0.0
                )
            else:
                visit.mobile_duration_minutes = 0.0

    @staticmethod
    def _geo_distance_meters(lat1, lon1, lat2, lon2):
        radius = 6371000.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
        return 2 * radius * math.asin(min(1.0, math.sqrt(a)))

    def _validate_mobile_location(self, latitude, longitude, accuracy):
        self.ensure_one()
        if latitude is None or longitude is None:
            raise UserError(_('Location is required for this mobile action.'))
        if not (-90 <= float(latitude) <= 90 and -180 <= float(longitude) <= 180):
            raise UserError(_('Invalid GPS coordinates.'))
        site = self.site_id
        if self.company_id.pestops_enforce_mobile_geofence and site.latitude and site.longitude:
            distance = self._geo_distance_meters(
                float(latitude), float(longitude), site.latitude, site.longitude
            )
            allowed = max(self.company_id.pestops_mobile_geofence_radius_meters or 250, 25)
            gps_accuracy = max(float(accuracy or 0), 0.0)
            if distance > allowed + gps_accuracy:
                raise UserError(
                    _('You are approximately %.0f m away from the site, outside the allowed mobile radius of %.0f m.')
                    % (distance, allowed)
                )
        return True

    def action_mobile_check_in(self, latitude, longitude, accuracy=0.0):
        for visit in self:
            if visit.state not in ('draft', 'scheduled'):
                raise UserError(_('Only draft or scheduled visits can be checked in.'))
            visit._validate_mobile_location(latitude, longitude, accuracy)
            now = fields.Datetime.now()
            visit.write({
                'state': 'in_progress',
                'actual_start': now,
                'mobile_checkin_used': True,
                'checkin_latitude': float(latitude),
                'checkin_longitude': float(longitude),
                'checkin_accuracy': float(accuracy or 0.0),
                'checkin_at': now,
            })
            visit.message_post(body=_(
                'Mobile check-in recorded at %s, GPS accuracy %.0f m.'
            ) % (now, float(accuracy or 0.0)))
            visit._ensure_project_task()
        return True

    def action_mobile_save_signature(self, signature, signer_name=False, note=False):
        for visit in self:
            if visit.state != 'in_progress':
                raise UserError(_('A customer signature can only be recorded on an active visit.'))
            if not signature:
                raise UserError(_('Please capture the customer signature before saving.'))
            visit.write({
                'customer_signature': signature,
                'customer_signature_name': signer_name or False,
                'customer_signature_date': fields.Datetime.now(),
                'customer_signature_note': note or False,
            })
            visit.message_post(body=_(
                'Customer signature recorded by %s.'
            ) % (signer_name or _('the customer')))
        return True

    def action_mobile_complete(self, latitude, longitude, accuracy=0.0, signature=False, signer_name=False, note=False):
        for visit in self:
            if visit.state != 'in_progress':
                raise UserError(_('Only visits in progress can be completed.'))
            visit._validate_mobile_location(latitude, longitude, accuracy)
            if self.company_id.pestops_require_customer_signature_before_close and not signature and not visit.customer_signature:
                raise UserError(_('A customer signature is required before completing this visit.'))
            if signature:
                visit.write({
                    'customer_signature': signature,
                    'customer_signature_name': signer_name or False,
                    'customer_signature_date': fields.Datetime.now(),
                    'customer_signature_note': note or False,
                })
            visit.write({
                'checkout_latitude': float(latitude),
                'checkout_longitude': float(longitude),
                'checkout_accuracy': float(accuracy or 0.0),
                'checkout_at': fields.Datetime.now(),
            })
            visit.action_done()
            visit.message_post(body=_('Mobile check-out recorded and visit completed.'))
        return True

    @api.depends('inspection_ids', 'treatment_ids', 'reservice_ids', 'anomaly_ids.state')
    def _compute_counts(self):
        for visit in self:
            visit.inspection_count = len(visit.inspection_ids)
            visit.treatment_count = len(visit.treatment_ids)
            visit.reservice_count = len(visit.reservice_ids)
            visit.anomaly_count = len(visit.anomaly_ids)
            visit.open_anomaly_count = len(visit.anomaly_ids.filtered(lambda a: a.state in ('open', 'in_progress')))

    @api.constrains('scheduled_start', 'scheduled_end')
    def _check_schedule(self):
        for visit in self:
            if visit.scheduled_start and visit.scheduled_end and visit.scheduled_end < visit.scheduled_start:
                raise ValidationError(_('Scheduled end must be after scheduled start.'))

    @api.model
    def _cron_generate_recurring_visits(self):
        plans = self.env['pest.treatment.plan'].search([
            ('active', '=', True),
            ('start_date', '<=', fields.Date.context_today(self)),
        ])
        plans.action_generate_visits()
        return True

    @api.model
    def _cron_visit_reminders(self):
        today = fields.Datetime.now()
        due_soon = today + timedelta(hours=max(self.env.company.pestops_visit_reminder_hours or 24, 1))
        visits = self.search([
            ('state', '=', 'scheduled'),
            ('scheduled_start', '>=', today),
            ('scheduled_start', '<=', due_soon),
            ('technician_id', '!=', False),
        ])
        for visit in visits:
            activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
            if not activity_type:
                continue
            existing = self.env['mail.activity'].search_count([
                ('res_model', '=', 'pest.visit'),
                ('res_id', '=', visit.id),
                ('activity_type_id', '=', activity_type.id),
                ('summary', '=', 'Upcoming PestOps Visit'),
            ])
            if not existing:
                self.env['mail.activity'].create({
                    'activity_type_id': activity_type.id,
                    'res_model_id': self.env['ir.model']._get_id('pest.visit'),
                    'res_id': visit.id,
                    'user_id': visit.technician_id.id,
                    'summary': 'Upcoming PestOps Visit',
                    'note': f'Visit {visit.name} is scheduled within the next 24 hours.',
                    'date_deadline': fields.Date.context_today(self),
                })
        return True

    def action_schedule(self):
        for visit in self:
            if visit.state != 'draft':
                continue
            visit.write({'state': 'scheduled'})
            visit._ensure_project_task()

    def action_start(self):
        for visit in self:
            if visit.state not in ('draft', 'scheduled'):
                raise UserError(_('Only draft or scheduled visits can be started.'))
            visit.write({
                'state': 'in_progress',
                'actual_start': fields.Datetime.now(),
            })
            visit._ensure_project_task()

    def _create_anomalies_from_inspections(self):
        Anomaly = self.env['pest.anomaly']
        for visit in self:
            for line in visit.inspection_ids.mapped('line_ids').filtered(lambda l: l.action_required):
                existing = Anomaly.search([
                    ('inspection_line_id', '=', line.id),
                    ('state', '!=', 'cancelled'),
                ], limit=1)
                if existing:
                    continue
                level_map = {
                    'none': 'low',
                    'low': 'low',
                    'medium': 'medium',
                    'high': 'high',
                    'critical': 'critical',
                }
                severity = level_map.get(line.activity_level, 'medium')
                Anomaly.create({
                    'visit_id': visit.id,
                    'inspection_id': line.inspection_id.id,
                    'inspection_line_id': line.id,
                    'zone_id': line.control_point_id.zone_id.id,
                    'control_point_id': line.control_point_id.id,
                    'pest_id': line.pest_id.id if line.pest_id else False,
                    'severity': severity,
                    'description': line.observation or _('Action required at control point %s.') % line.control_point_id.display_name,
                    'recommendation': getattr(line, 'recommended_action', False) or False,
                    'due_date': fields.Date.context_today(self) if severity in ('high', 'critical') else False,
                    'attachment_image': line.image_1920 or False,
                })

    def _prepare_completion(self):
        for visit in self:
            if visit.inspection_required and not visit.inspection_ids:
                raise UserError(_('At least one inspection is required before completing this visit.'))
            if visit.treatment_required and not visit.treatment_ids:
                raise UserError(_('At least one treatment is required before completing this visit.'))
            if not visit.actual_start:
                raise UserError(_('The visit must be started before it can be completed.'))
            if self.company_id.pestops_require_customer_signature_before_close and not visit.customer_signature:
                raise UserError(_('A customer signature is required before completing this visit.'))

    def action_done(self):
        for visit in self:
            if visit.state != 'in_progress':
                raise UserError(_('Only visits in progress can be completed.'))
            visit._prepare_completion()
            visit._create_anomalies_from_inspections()
            open_anomalies = visit.anomaly_ids.filtered(lambda a: a.state in ('open', 'in_progress'))
            critical = visit.anomaly_ids.filtered(lambda a: a.severity == 'critical' and a.state != 'cancelled')
            outcome = 'critical' if critical else ('follow_up' if open_anomalies else 'normal')
            summary = _('Completed with %s open anomaly(ies).') % len(open_anomalies) if open_anomalies else _('Visit completed successfully.')
            visit.write({
                'state': 'done',
                'actual_end': fields.Datetime.now(),
                'completion_outcome': outcome,
                'completion_summary': summary,
            })

    def action_cancel(self):
        for visit in self:
            if visit.state == 'done':
                raise UserError(_('A completed visit cannot be cancelled.'))
            visit.write({'state': 'cancelled'})

    def action_create_inspection(self):
        self.ensure_one()
        inspection = self.env['pest.inspection'].create({
            'visit_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection'),
            'res_model': 'pest.inspection',
            'view_mode': 'form',
            'res_id': inspection.id,
            'target': 'current',
        }

    def action_create_treatment(self):
        self.ensure_one()
        treatment = self.env['pest.treatment'].create({
            'visit_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Treatment'),
            'res_model': 'pest.treatment',
            'view_mode': 'form',
            'res_id': treatment.id,
            'target': 'current',
        }

    def _ensure_project_task(self):
        ProjectTask = self.env['project.task']
        Project = self.env['project.project']

        for visit in self.filtered(lambda v: not v.task_id):
            project = Project.search([
                ('company_id', 'in', [visit.company_id.id, False]),
                ('name', '=', 'PestOps Visits'),
            ], limit=1)

            if not project:
                project = Project.create({
                    'name': 'PestOps Visits',
                    'company_id': visit.company_id.id,
                })

            vals = {
                'name': f'{visit.name} - {visit.site_id.name}',
                'project_id': project.id,
                'partner_id': visit.site_id.partner_id.id,
                'description': visit.notes or False,
            }
            if visit.technician_id:
                vals['user_ids'] = [(6, 0, [visit.technician_id.id])]
            task = ProjectTask.create(vals)
            visit.task_id = task.id

    def action_view_anomalies(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Visit Anomalies'),
            'res_model': 'pest.anomaly',
            'view_mode': 'list,form',
            'domain': [('visit_id', '=', self.id)],
            'context': {'default_visit_id': self.id},
        }

    def action_view_task(self):
        self.ensure_one()
        if not self.task_id:
            self._ensure_project_task()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Visit Task'),
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': self.task_id.id,
        }
