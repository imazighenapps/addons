# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EduflowTimetableSession(models.Model):
    _name = 'eduflow.timetable.session'
    _description = "Timetable Session"
    _inherit = ['mail.thread']
    _order = 'day, hour_start'

    classroom_id = fields.Many2one('eduflow.classroom', string="Class", required=True, tracking=True)
    subject_id = fields.Many2one('eduflow.subject', string="Subject", required=True, tracking=True)
    teacher_id = fields.Many2one('eduflow.teacher', string="Teacher", required=True, tracking=True)
    room = fields.Char(string="Room (Legacy)")
    room_id = fields.Many2one('eduflow.room', string="Room")
    locked = fields.Boolean(string="Locked", default=False, help="If locked, generation will not overwrite")
    day = fields.Selection([
        ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
        ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday'),
    ], string="Day", required=True)
    hour_start = fields.Float(string="Start Time", required=True)
    hour_end = fields.Float(string="End Time", required=True)
    company_id = fields.Many2one('res.company', string="Institution",
                                  related='classroom_id.company_id', store=True, readonly=True)

    # F2.4 -- non-stored datetime projection of the weekly slot onto the
    # current calendar week, used only so the standard Odoo Calendar widget
    # (which requires a Datetime field) can display the weekly timetable.
    # The session itself remains defined by day/hour_start/hour_end.
    date_start = fields.Datetime(string="Start", compute='_compute_calendar_dates')
    date_stop = fields.Datetime(string="End", compute='_compute_calendar_dates')

    @api.depends('day', 'hour_start', 'hour_end')
    def _compute_calendar_dates(self):
        today = fields.Date.context_today(self)
        monday = today - timedelta(days=today.weekday())
        for rec in self:
            if not rec.day:
                rec.date_start = False
                rec.date_stop = False
                continue
            day_date = monday + timedelta(days=int(rec.day))
            day_start = datetime.combine(day_date, datetime.min.time())
            rec.date_start = day_start + timedelta(hours=rec.hour_start or 0.0)
            rec.date_stop = day_start + timedelta(hours=rec.hour_end or 0.0)

    @api.constrains('day', 'hour_start', 'hour_end', 'teacher_id', 'classroom_id', 'room')
    def _check_conflicts(self):
        for rec in self:
            if rec.hour_start >= rec.hour_end:
                raise ValidationError("End time must be after start time.")

            domain_base = [
                ('id', '!=', rec.id),
                ('day', '=', rec.day),
                ('hour_start', '<', rec.hour_end),
                ('hour_end', '>', rec.hour_start),
            ]
            if rec.company_id:
                domain_base.append(('company_id', '=', rec.company_id.id))

            # Conflict: teacher assigned to two classes at the same time
            teacher_conflict = self.search(domain_base + [('teacher_id', '=', rec.teacher_id.id)])
            if teacher_conflict:
                raise ValidationError(
                    "Conflict detected: teacher %s is already assigned to another session "
                    "in this time slot." % rec.teacher_id.name)

            # Conflict: class has two simultaneous courses
            classroom_conflict = self.search(
                domain_base + [('classroom_id', '=', rec.classroom_id.id)])
            if classroom_conflict:
                raise ValidationError(
                    "Conflict detected: class %s already has a course in this time slot."
                    % rec.classroom_id.name)

            # Conflict: room used simultaneously (legacy Char and new Many2one)
            if rec.room:
                room_conflict = self.search(domain_base + [('room', '=', rec.room)])
                if room_conflict:
                    raise ValidationError(
                        "Conflict detected: room %s is already occupied in this time slot."
                        % rec.room)
            if rec.room_id:
                room_id_conflict = self.search(domain_base + [('room_id', '=', rec.room_id.id)])
                if room_id_conflict:
                    raise ValidationError(
                        "Conflict detected: room %s is already occupied in this time slot." % rec.room_id.name)
