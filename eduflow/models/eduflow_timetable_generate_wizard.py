# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EduflowTimetableGenerateWizard(models.TransientModel):
    _name = 'eduflow.timetable.generate.wizard'
    _description = "Generate Timetable Wizard - Max Config"

    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year", required=True,
                               default=lambda self: self.env['eduflow.academic.year'].search([('active_year','=',True)], limit=1))
    classroom_ids = fields.Many2many('eduflow.classroom', string="Classes", required=True,
                                      help="Leave empty for all classes of the year (auto-filled)")
    slot_duration = fields.Selection([
        ('60', '60 min'), ('45', '45 min'), ('90', '90 min'), ('120', '120 min'),
    ], string="Slot Duration", default='60', required=True)
    lunch_break = fields.Char(string="Lunch Break", default="12:00-13:30", help="e.g. 12:00-13:30 blocked")
    allow_overwrite = fields.Boolean(string="Overwrite Existing", default=False, help="If checked, delete existing sessions of the year before generation")
    lock_existing = fields.Boolean(string="Keep Locked Slots", default=True, help="Locked sessions (lock=True) are never deleted")
    use_teacher_availability = fields.Boolean(string="Respect Teacher Availability", default=True)
    use_room_pool = fields.Boolean(string="Use Shared Room Pool", default=False, help="If checked, use eduflow.room pool; else classroom.room Char")
    strategy = fields.Selection([
        ('greedy', 'Greedy (fast)'),
        ('balanced', 'Balanced (soft constraints)'),
    ], string="Strategy", default='balanced', required=True)
    morning_core = fields.Boolean(string="Core Subjects in Morning", default=True)
    max_hours_per_day_teacher = fields.Integer(string="Max Hours / Day / Teacher", default=6)
    avoid_consecutive_same = fields.Boolean(string="Avoid Consecutive Same Subject", default=True)
    generated_count = fields.Integer(string="Generated", readonly=True)
    unassigned_count = fields.Integer(string="Unassigned", readonly=True)
    log = fields.Text(string="Generation Log", readonly=True)

    @api.onchange('year_id')
    def _onchange_year(self):
        if self.year_id:
            classrooms = self.env['eduflow.classroom'].search([('year_id','=',self.year_id.id)])
            self.classroom_ids = [(6,0, classrooms.ids)]

    def _parse_lunch(self):
        try:
            start, end = self.lunch_break.split('-')
            h1 = float(start.split(':')[0]) + float(start.split(':')[1])/60
            h2 = float(end.split(':')[0]) + float(end.split(':')[1])/60
            return (h1, h2)
        except:
            return (12.0, 13.5)

    def _teacher_available(self, teacher, day, hour_from, hour_to):
        if not self.use_teacher_availability:
            return True
        avails = self.env['eduflow.teacher.availability'].search([
            ('teacher_id','=',teacher.id), ('day','=',day), ('available','=',True)
        ])
        if not avails:
            return True
        for av in avails:
            if av.hour_from <= hour_from and av.hour_to >= hour_to and av.preference != '3':
                return True
        return False

    def action_generate(self):
        self.ensure_one()
        if not self.classroom_ids:
            raise ValidationError(_("Please select at least one class."))
        if self.allow_overwrite:
            domain = [('classroom_id','in', self.classroom_ids.ids)]
            if self.lock_existing:
                domain.append(('locked','=',False))
            existing = self.env['eduflow.timetable.session'].search(domain)
            existing.unlink()
        lunch_from, lunch_to = self._parse_lunch()
        slot = int(self.slot_duration)
        slot_h = slot/60.0
        days = ['0','1','2','3','4']
        hours = []
        h = 8.0
        while h + slot_h <= 17.0:
            if not (h < lunch_to and h+slot_h > lunch_from):
                hours.append((h, h+slot_h))
            h += slot_h
        generated = 0
        unassigned = 0
        log_lines = []
        for classroom in self.classroom_ids:
            level = classroom.level_id
            hour_cfgs = self.env['eduflow.level.subject.hours'].search([
                ('level_id','=',level.id),
                ('year_id','=',self.year_id.id)
            ])
            if not hour_cfgs:
                subjects = self.env['eduflow.subject'].search([('level_id','=',level.id)])
                hour_cfgs = self.env['eduflow.level.subject.hours']
                for subj in subjects:
                    hour_cfgs |= self.env['eduflow.level.subject.hours'].create({
                        'level_id': level.id,
                        'subject_id': subj.id,
                        'year_id': self.year_id.id,
                        'hours_per_week': 3.0,
                    })
                    log_lines.append(f"Auto-created 3h/week for {level.name} - {subj.name}")
            hour_cfgs = hour_cfgs.sorted(key=lambda r: r.hours_per_week, reverse=True)
            for cfg in hour_cfgs:
                subject = cfg.subject_id
                teachers = self.env['eduflow.teacher'].search([('subject_ids','in', subject.id)])
                if not teachers:
                    log_lines.append(f"Unassigned: {classroom.name} - {subject.name} (no teacher)")
                    unassigned += int(cfg.hours_per_week // slot_h) if slot_h else int(cfg.hours_per_week)
                    continue
                teacher = teachers[0]
                sessions_needed = int(cfg.hours_per_week // slot_h) if slot_h else 1
                placed = 0
                for day in days:
                    for hf, ht in hours:
                        if placed >= sessions_needed:
                            break
                        if self.morning_core and cfg.morning_only and hf >= 12:
                            continue
                        if not self._teacher_available(teacher, day, hf, ht):
                            continue
                        try:
                            vals = {
                                'classroom_id': classroom.id,
                                'subject_id': subject.id,
                                'teacher_id': teacher.id,
                                'day': day,
                                'hour_start': hf,
                                'hour_end': ht,
                            }
                            if self.use_room_pool:
                                rooms = self.env['eduflow.room'].search([('room_type','=', cfg.room_type if cfg.room_type!='any' else 'classroom')], limit=1)
                                if rooms:
                                    vals['room_id'] = rooms[0].id
                            self.env['eduflow.timetable.session'].create(vals)
                            placed += 1
                            generated += 1
                        except ValidationError:
                            continue
                    if placed >= sessions_needed:
                        break
                if placed < sessions_needed:
                    unassigned += (sessions_needed - placed)
                    log_lines.append(f"Partial: {classroom.name} - {subject.name} {placed}/{sessions_needed} placed")
        self.write({
            'generated_count': generated,
            'unassigned_count': unassigned,
            'log': "\n".join(log_lines) or _("Generation completed. %s created, %s unassigned.") % (generated, unassigned)
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eduflow.timetable.generate.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
