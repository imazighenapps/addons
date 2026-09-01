# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EduflowEnrollment(models.Model):
    _name = 'eduflow.enrollment'
    _description = "Enrollment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year_id desc, student_id'

    student_id = fields.Many2one('eduflow.student', string="Student", required=True, tracking=True)
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year", required=True,
                               tracking=True)
    level_id = fields.Many2one('eduflow.level', string="Level", required=True)
    classroom_id = fields.Many2one('eduflow.classroom', string="Class", tracking=True,
                                    domain="[('year_id', '=', year_id), ('level_id', '=', level_id)]")
    section = fields.Char(string="Section")
    date = fields.Date(string="Enrollment Date", default=fields.Date.context_today)
    regime = fields.Selection([
        ('day', 'Day Student'),
        ('half_board', 'Half Board'),
        ('boarding', 'Boarding'),
    ], string="School Regime", default='day')
    enrollment_type = fields.Selection([
        ('new', 'New Enrollment'),
        ('renewal', 'Re-enrollment'),
        ('transfer', 'Transfer'),
    ], string="Enrollment Type", default='new')
    admission_id = fields.Many2one('eduflow.admission', string="Related Admission")
    registration_fee = fields.Monetary(string="Registration Fee", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='draft', required=True, tracking=True)
    classroom_history_ids = fields.One2many('eduflow.enrollment.classroom.history', 'enrollment_id',
                                             string="Classroom Change History")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.constrains('classroom_id')
    def _check_classroom_capacity(self):
        for rec in self:
            if rec.classroom_id and rec.state in ('confirmed', 'active'):
                domain = [
                    ('classroom_id', '=', rec.classroom_id.id),
                    ('state', 'in', ('confirmed', 'active')),
                ]
                if rec.company_id:
                    domain.append(('company_id', '=', rec.company_id.id))
                count = self.search_count(domain)
                if count > rec.classroom_id.capacity:
                    raise ValidationError(
                        "Maximum capacity of class '%s' (%s seats) has been reached."
                        % (rec.classroom_id.name, rec.classroom_id.capacity))

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        for rec in self:
            rec.student_id.write({'status': 'enrolled'})

    def action_activate(self):
        self.write({'state': 'active'})
        for rec in self:
            rec.student_id.write({'status': 'active'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_change_classroom(self):
        """F5 — simplified classroom change (audit 2026-08-31): opens the
        enrollment form in a dialog. The actual history is logged
        automatically in `write()` via `classroom_history_ids`; no dedicated
        wizard model is required for the current MVP. If a full wizard
        (old/new class + reason) is needed later, replace this method with
        a TransientModel wizard consuming `default_enrollment_id`."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eduflow.enrollment',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'default_enrollment_id': self.id},
        }

    def write(self, vals):
        if 'classroom_id' in vals:
            for rec in self:
                old_classroom = rec.classroom_id
                new_classroom_id = vals['classroom_id']
                if old_classroom.id != new_classroom_id and old_classroom:
                    self.env['eduflow.enrollment.classroom.history'].create({
                        'enrollment_id': rec.id,
                        'old_classroom_id': old_classroom.id,
                        'new_classroom_id': new_classroom_id,
                        'change_date': fields.Date.context_today(rec),
                        'user_id': self.env.user.id,
                    })
        return super().write(vals)

    def action_renew_next_year(self):
        """Quick re-enrollment for the next year."""
        self.ensure_one()
        next_year = self.env['eduflow.academic.year'].search(
            [('date_start', '>', self.year_id.date_start)],
            order='date_start asc', limit=1)
        if not next_year:
            raise ValidationError("No next academic year has been created.")
        new_enrollment = self.copy({
            'year_id': next_year.id,
            'classroom_id': False,
            'state': 'draft',
            'enrollment_type': 'renewal',
            'date': fields.Date.context_today(self),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eduflow.enrollment',
            'view_mode': 'form',
            'res_id': new_enrollment.id,
        }


class EduflowEnrollmentClassroomHistory(models.Model):
    _name = 'eduflow.enrollment.classroom.history'
    _description = "Classroom Change History"
    _order = 'change_date desc'

    enrollment_id = fields.Many2one('eduflow.enrollment', required=True, ondelete='cascade')
    old_classroom_id = fields.Many2one('eduflow.classroom', string="Previous Class")
    new_classroom_id = fields.Many2one('eduflow.classroom', string="New Class")
    change_date = fields.Date(string="Change Date")
    user_id = fields.Many2one('res.users', string="Performed by")
