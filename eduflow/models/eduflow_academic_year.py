# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EduflowAcademicYear(models.Model):
    _name = 'eduflow.academic.year'
    _description = "Academic Year"
    _inherit = ['mail.thread']
    _order = 'date_start desc'

    name = fields.Char(string="Academic Year", required=True, help="Ex: 2026/2027")
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('close', 'Closed'),
    ], string="Status", default='draft', required=True, tracking=True)
    active_year = fields.Boolean(string="Active Year", default=False)
    period_ids = fields.One2many('eduflow.academic.period', 'year_id', string="Periods")
    company_id = fields.Many2one('res.company', string="Institution",
                                  default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)',
         "This academic year already exists for this institution."),
    ]

    @api.constrains('active_year', 'company_id')
    def _check_single_active_year(self):
        for rec in self:
            if rec.active_year:
                other = self.search([
                    ('active_year', '=', True),
                    ('company_id', '=', rec.company_id.id),
                    ('id', '!=', rec.id),
                ])
                if other:
                    raise ValidationError(
                        "Only one active academic year is allowed per institution. "
                        "Please deactivate '%s' before activating this one." % other[0].name)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start >= rec.date_end:
                raise ValidationError("End date must be after start date.")

    def action_open(self):
        self.write({'state': 'open'})

    def action_close(self):
        self.write({'state': 'close', 'active_year': False})

    def action_set_draft(self):
        self.write({'state': 'draft'})
