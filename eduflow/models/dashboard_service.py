# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date

class DashboardEducation(models.AbstractModel):
    """Service Dashboard EduFlow Pro — AbstractModel, pas de table."""
    _name = 'dashboard.education'
    _description = 'Service Dashboard EduFlow'

    @api.model
    def get_enrollment_kpis(self, year_id=None):
        domain = [('year_id','=',year_id)] if year_id else []
        enrollments = self.env['eduflow.enrollment'].search(domain + [('state','in',('confirmed','active'))])
        classrooms = self.env['eduflow.classroom'].search([('year_id','=',year_id)] if year_id else [])
        caps = sum(classrooms.mapped('capacity'))
        return {
            'total_students': len(enrollments.mapped('student_id')),
            'total_classrooms': len(classrooms),
            'fill_rate': round(len(enrollments.mapped('student_id'))/caps*100,1) if caps else 0,
            'pending_admissions': self.env['eduflow.admission'].search_count([('state','in',('new','review','interview'))] + ([('year_id','=',year_id)] if year_id else [])),
        }

    @api.model
    def get_finance_kpis(self, year_id=None):
        domain = [('year_id','=',year_id)] if year_id else []
        fees = self.env['eduflow.fee'].search(domain)
        invoiced = sum(fees.mapped('amount'))
        collected = sum(fees.mapped('paid_amount'))
        outstanding = sum(fees.mapped('remaining_amount'))
        overdue = self.env['eduflow.fee'].search_count(domain + [('state','=','overdue')])
        return {
            'invoiced': invoiced,
            'collected': collected,
            'outstanding': outstanding,
            'overdue_count': overdue,
            'collection_rate': round(collected/invoiced*100,1) if invoiced else 0,
        }

    @api.model
    def get_attendance_kpis(self, year_id=None):
        enrollments = self.env['eduflow.enrollment'].search([('year_id','=',year_id),('state','in',('confirmed','active'))] if year_id else [('state','in',('confirmed','active'))])
        student_ids = enrollments.mapped('student_id').ids
        attendances = self.env['eduflow.attendance'].search([('student_id','in',student_ids)]) if student_ids else self.env['eduflow.attendance']
        total = len(attendances)
        absent = len(attendances.filtered(lambda a: a.state=='absent'))
        today = fields.Date.context_today(self)
        present_today = len(attendances.filtered(lambda a: a.date==today and a.state=='present'))
        return {
            'total': total,
            'absent': absent,
            'present_today': present_today,
            'absenteeism': round(absent/total*100,2) if total else 0,
        }

    @api.model
    def get_grades_kpis(self, year_id=None):
        domain = [('year_id','=',year_id)] if year_id else []
        cards = self.env['eduflow.report.card'].search(domain)
        avg = round(sum(cards.mapped('general_average'))/len(cards),2) if cards else 0
        # Top 5 classes by avg
        classrooms = self.env['eduflow.classroom'].search([('year_id','=',year_id)] if year_id else [])
        class_avgs = []
        for cls in classrooms:
            cls_cards = cards.filtered(lambda c: c.classroom_id.id==cls.id)
            if cls_cards:
                class_avgs.append({'name': cls.name, 'avg': round(sum(cls_cards.mapped('general_average'))/len(cls_cards),2)})
        class_avgs = sorted(class_avgs, key=lambda x: x['avg'], reverse=True)[:5]
        return {'average': avg, 'top_classes': class_avgs, 'count': len(cards)}

    @api.model
    def get_enrollment_by_level(self, year_id=None):
        # Handle year_id as string or int, and ensure demo data is included even if year is None
        try:
            year_id = int(year_id) if year_id else None
        except:
            year_id = None
        levels = self.env['eduflow.level'].search([])
        result=[]
        for lvl in levels:
            domain = [('level_id','=',lvl.id),('state','in',('confirmed','active'))]
            if year_id:
                domain.append(('year_id','=',year_id))
            count=self.env['eduflow.enrollment'].search_count(domain)
            # Always include level even if count is 0 for better UX, but filter out 0 for now to avoid empty
            result.append({'level': lvl.name, 'count': count})
        # Filter out zero counts for cleaner graph, but keep at least 1
        filtered = [r for r in result if r['count']>0]
        return filtered if filtered else result[:3]

    @api.model
    def get_fees_by_month(self, year=None, year_id=None):
        # Try to use academic year if provided, else calendar year
        if year_id:
            try:
                year_id=int(year_id)
                year_rec=self.env['eduflow.academic.year'].browse(year_id)
                if year_rec.exists() and year_rec.date_start:
                    year=year_rec.date_start.year
            except:
                pass
        if not year:
            year=date.today().year
        months=['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
        res=[]
        for m in range(1,13):
            first=date(year,m,1)
            last=date(year,12,31) if m==12 else date(year,m+1,1)-timedelta(days=1)
            # Filter by academic year if provided
            domain=[('due_date','>=',first),('due_date','<=',last)]
            if year_id:
                domain.append(('year_id','=',year_id))
            fees=self.env['eduflow.fee'].search(domain)
            res.append({'month':months[m-1],'invoiced':sum(fees.mapped('amount')),'collected':sum(fees.mapped('paid_amount'))})
        return res

    @api.model
    def get_student_kpis(self, year_id=None):
        domain = [('year_id','=',year_id)] if year_id else []
        students = self.env['eduflow.student'].search([])
        enrollments = self.env['eduflow.enrollment'].search(domain + [('state','in',('confirmed','active'))])
        s_ids = enrollments.mapped('student_id').ids
        return {
            'total': len(students),
            'active': len(s_ids),
            'by_gender': [
                {'label': 'Male', 'count': self.env['eduflow.student'].search_count([('gender','=','m')] + ([('id','in',s_ids)] if s_ids else []))},
                {'label': 'Female', 'count': self.env['eduflow.student'].search_count([('gender','=','f')] + ([('id','in',s_ids)] if s_ids else []))},
            ],
            'by_status': [{'label': s, 'count': self.env['eduflow.student'].search_count([('status','=',s)])} for s in ['prospect','waiting','enrolled','active']],
        }

    @api.model
    def get_teacher_kpis(self):
        teachers = self.env['eduflow.teacher'].search([])
        by_specialty = {}
        for t in teachers:
            key = t.specialty or 'Unknown'
            by_specialty[key] = by_specialty.get(key,0)+1
        return {
            'total': len(teachers),
            'active': len(teachers.filtered(lambda t: t.status=='active')),
            'by_specialty': [{'specialty': k, 'count': v} for k,v in sorted(by_specialty.items(), key=lambda x: x[1], reverse=True)[:6]],
        }

    @api.model
    def get_classroom_kpis(self, year_id=None):
        domain = [('year_id','=',year_id)] if year_id else []
        rooms = self.env['eduflow.classroom'].search(domain)
        data=[]
        for r in rooms:
            enrolled = self.env['eduflow.enrollment'].search_count([('classroom_id','=',r.id),('state','in',('confirmed','active'))] + ([('company_id','=',r.company_id.id)] if r.company_id else []))
            data.append({'name': r.name, 'capacity': r.capacity, 'enrolled': enrolled, 'rate': round(enrolled/r.capacity*100,1) if r.capacity else 0})
        return sorted(data, key=lambda x: x['rate'], reverse=True)[:10]

    @api.model
    def get_admission_kpis(self, year_id=None):
        domain = [('year_id','=',year_id)] if year_id else []
        return {s: self.env['eduflow.admission'].search_count(domain+[('state','=',s)]) for s in ['new','review','interview','accepted','refused','enrolled']}

    @api.model
    def get_exam_kpis(self, year_id=None):
        domain = [('year_id','=',year_id)] if year_id else []
        return {
            'total': self.env['eduflow.exam'].search_count(domain),
            'by_state': [{'label': s, 'count': self.env['eduflow.exam'].search_count(domain+[('state','=',s)])} for s in ['draft','grading','validated']],
        }

    @api.model
    def get_dashboard_data(self, year_id=None):
        # Handle year_id as string from frontend
        try:
            year_id = int(year_id) if year_id else None
        except:
            year_id = None
        # Fallback to active year if none provided and no data found
        if not year_id:
            active = self.env['eduflow.academic.year'].search([('active_year','=',True)], limit=1)
            if active:
                year_id = active.id
        data = {
            'enrollment': self.get_enrollment_kpis(year_id),
            'finance': self.get_finance_kpis(year_id),
            'attendance': self.get_attendance_kpis(year_id),
            'grades': self.get_grades_kpis(year_id),
            'by_level': self.get_enrollment_by_level(year_id),
            'fees_by_month': self.get_fees_by_month(year_id=year_id),
            'students': self.get_student_kpis(year_id),
            'teachers': self.get_teacher_kpis(),
            'classrooms': self.get_classroom_kpis(year_id),
            'admissions': self.get_admission_kpis(year_id),
            'exams': self.get_exam_kpis(year_id),
            'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M'),
        }
        # Ensure at least some data for demo: if all zero, try without year filter
        if not data['by_level'] or all(x['count']==0 for x in data['by_level']):
            data['by_level'] = self.get_enrollment_by_level(None)
        if not data['fees_by_month'] or all(x['invoiced']==0 for x in data['fees_by_month']):
            data['fees_by_month'] = self.get_fees_by_month(year=None)
        return data
