from odoo import api, fields, models


class PestSite(models.Model):
    _name = 'pest.site'
    _description = 'Pest Control Site'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, id'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.site'),
        copy=False,
        readonly=True,
    )
    active = fields.Boolean(default=True, tracking=True)

    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        string='Customer',
        ondelete='restrict',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    state_id = fields.Many2one('res.country.state')
    country_id = fields.Many2one('res.country')

    latitude = fields.Float(digits=(10, 7))
    longitude = fields.Float(digits=(10, 7))

    site_type = fields.Selection(
        [
            ('hotel', 'Hotel'),
            ('restaurant', 'Restaurant'),
            ('industry', 'Industrial'),
            ('warehouse', 'Warehouse'),
            ('retail', 'Retail'),
            ('healthcare', 'Healthcare'),
            ('education', 'Education'),
            ('office', 'Office'),
            ('residential', 'Residential'),
            ('other', 'Other'),
        ],
        default='other',
    )

    risk_level_id = fields.Many2one('pest.risk.level', ondelete='restrict')
    responsible_id = fields.Many2one(
        'res.users',
        string='Operational Responsible',
        default=lambda self: self.env.user,
    )

    zone_ids = fields.One2many('pest.zone', 'site_id')
    control_point_ids = fields.One2many('pest.control.point', 'site_id')
    plan_ids = fields.One2many('pest.treatment.plan', 'site_id')
    visit_ids = fields.One2many('pest.visit', 'site_id')

    last_visit_date = fields.Datetime(compute='_compute_visit_dates', store=True)
    next_visit_date = fields.Datetime(compute='_compute_visit_dates', store=True)
    visit_count = fields.Integer(compute='_compute_counts')
    open_reservice_count = fields.Integer(compute='_compute_counts')

    notes = fields.Html()
    image_1920 = fields.Image()

    @api.depends('visit_ids.scheduled_start', 'visit_ids.state')
    def _compute_visit_dates(self):
        for site in self:
            done_visits = site.visit_ids.filtered(lambda v: v.state == 'done' and v.actual_start)
            future_visits = site.visit_ids.filtered(
                lambda v: v.state in ('draft', 'scheduled') and v.scheduled_start
            )
            site.last_visit_date = max(done_visits.mapped('actual_start'), default=False)
            site.next_visit_date = min(future_visits.mapped('scheduled_start'), default=False)

    def _compute_counts(self):
        for site in self:
            site.visit_count = len(site.visit_ids)
            site.open_reservice_count = len(
                site.visit_ids.mapped('reservice_ids').filtered(
                    lambda r: r.state in ('draft', 'open', 'in_progress')
                )
            )


    def action_view_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'res_model': 'pest.visit',
            'view_mode': 'list,form,calendar',
            'domain': [('site_id', '=', self.id)],
        }

    def action_view_control_points(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Control Points',
            'res_model': 'pest.control.point',
            'view_mode': 'list,form',
            'domain': [('site_id', '=', self.id)],
        }

    def action_view_reservices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Re-Services',
            'res_model': 'pest.reservice',
            'view_mode': 'list,form',
            'domain': [('site_id', '=', self.id), ('state', 'not in', ('done', 'cancelled'))],
        }
