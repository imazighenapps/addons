# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

PAGE_SIZE = 20


class EduflowParentPortal(CustomerPortal):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _eduflow_is_parent(self):
        """True si l'utilisateur courant appartient au groupe portail parent."""
        return request.env.user.has_group('eduflow.group_eduflow_parent_portal')

    def _eduflow_get_children(self):
        """Return students accessible to the logged-in parent.
        Relies entirely on existing ir.rule: a simple
        search([]) will therefore return only the current parent's children."""
        if not self._eduflow_is_parent():
            return request.env['eduflow.student']
        return request.env['eduflow.student'].search([])

    def _eduflow_get_child(self, child_id):
        """Return the requested student if the logged-in parent has access,
        otherwise raise MissingError (-> 404) to not reveal existence
        of the record to an unauthorized user."""
        child_sudo = request.env['eduflow.student'].sudo().browse(child_id).exists()
        if not child_sudo:
            raise MissingError(_("This student does not exist."))
        child = request.env['eduflow.student'].browse(child_id)
        try:
            child.check_access('read')
        except AccessError:
            raise MissingError(_("This student does not exist."))
        return child

    # ------------------------------------------------------------------
    # Home portail : ajoute la carte "My Children"
    # ------------------------------------------------------------------
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if self._eduflow_is_parent() and 'eduflow_children_count' in counters:
            values['eduflow_children_count'] = len(self._eduflow_get_children())
        return values

    # ------------------------------------------------------------------
    # Liste des enfants
    # ------------------------------------------------------------------
    @http.route(['/my/children'], type='http', auth='user', website=True)
    def portal_my_children(self, **kw):
        if not self._eduflow_is_parent():
            return request.redirect('/my')
        children = self._eduflow_get_children()
        values = self._prepare_portal_layout_values()
        values.update({
            'children': children,
            'page_name': 'eduflow_children',
        })
        return request.render('eduflow.portal_my_children', values)

    # ------------------------------------------------------------------
    # Dashboard d'un enfant
    # ------------------------------------------------------------------
    @http.route(['/my/children/<int:child_id>'], type='http', auth='user', website=True)
    def portal_child_dashboard(self, child_id, page=1, **kw):
        try:
            child = self._eduflow_get_child(child_id)
        except MissingError:
            return request.redirect('/my/children')

        enrollment = child.current_enrollment_id
        classroom = enrollment.classroom_id

        # Current class timetable, grouped by day
        timetable_by_day = {}
        if classroom:
            sessions = request.env['eduflow.timetable.session'].search([
                ('classroom_id', '=', classroom.id),
            ], order='day, hour_start')
            for session in sessions:
                timetable_by_day.setdefault(session.day, request.env['eduflow.timetable.session'])
                timetable_by_day[session.day] |= session

        day_labels = [
            ('0', _('Monday')), ('1', _('Tuesday')), ('2', _('Wednesday')),
            ('3', _('Thursday')), ('4', _('Friday')), ('5', _('Saturday')), ('6', _('Sunday')),
        ]

        # Paginated attendance records (most recent first)
        attendance_domain = [('student_id', '=', child.id)]
        attendance_count = request.env['eduflow.attendance'].search_count(attendance_domain)
        pager = portal_pager(
            url=f"/my/children/{child.id}",
            total=attendance_count,
            page=page,
            step=PAGE_SIZE,
        )
        attendances = request.env['eduflow.attendance'].search(
            attendance_domain, order='date desc', limit=PAGE_SIZE, offset=pager['offset'])

        # Published report cards only (already filtered by ir.rule, we only
        # sort here)
        report_cards = request.env['eduflow.report.card'].search([
            ('student_id', '=', child.id),
        ], order='period_id desc')

        # Fees and Payments
        fees = request.env['eduflow.fee'].search([
            ('student_id', '=', child.id),
        ], order='due_date desc')

        values = self._prepare_portal_layout_values()
        values.update({
            'child': child,
            'enrollment': enrollment,
            'classroom': classroom,
            'day_labels': day_labels,
            'timetable_by_day': timetable_by_day,
            'attendances': attendances,
            'attendance_pager': pager,
            'report_cards': report_cards,
            'fees': fees,
            'page_name': 'eduflow_child_dashboard',
        })
        return request.render('eduflow.portal_child_dashboard', values)

    # ------------------------------------------------------------------
    # Report card download (PDF)
    # ------------------------------------------------------------------
    @http.route(['/my/children/<int:child_id>/report-card/<int:report_card_id>'],
                type='http', auth='user', website=True)
    def portal_report_card_pdf(self, child_id, report_card_id, **kw):
        try:
            child = self._eduflow_get_child(child_id)
        except MissingError:
            return request.redirect('/my/children')

        report_card = request.env['eduflow.report.card'].browse(report_card_id).exists()
        if (not report_card or report_card.student_id.id != child.id
                or report_card.state != 'published'):
            return request.redirect(f'/my/children/{child.id}')
        try:
            report_card.check_access('read')
        except AccessError:
            return request.redirect(f'/my/children/{child.id}')

        pdf_content, _ext = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'eduflow.action_report_eduflow_report_card', res_ids=[report_card.id])
        filename = f"Report Card - {report_card.student_id.display_name} - {report_card.period_id.name}.pdf"
        return request.make_response(pdf_content, headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', http.content_disposition(filename)),
        ])

    # ------------------------------------------------------------------
    # Payment Receipt (PDF)
    # ------------------------------------------------------------------
    @http.route(['/my/children/<int:child_id>/payment/<int:payment_id>'],
                type='http', auth='user', website=True)
    def portal_payment_receipt_pdf(self, child_id, payment_id, **kw):
        try:
            child = self._eduflow_get_child(child_id)
        except MissingError:
            return request.redirect('/my/children')

        payment = request.env['eduflow.payment'].browse(payment_id).exists()
        if not payment or payment.student_id.id != child.id:
            return request.redirect(f'/my/children/{child.id}')
        try:
            payment.check_access('read')
        except AccessError:
            return request.redirect(f'/my/children/{child.id}')

        pdf_content, _ext = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'eduflow.action_report_eduflow_payment_receipt', res_ids=[payment.id])
        filename = f"Recu - {payment.name}.pdf"
        return request.make_response(pdf_content, headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', http.content_disposition(filename)),
        ])


class EduflowTeacherPortal(CustomerPortal):
    """F3.2 -- lightweight self-service space for teachers: their weekly
    timetable and the list of their classes, with a direct link back to
    the 'Take Attendance' assistant (F2.1) for each class."""

    def _eduflow_get_teacher(self):
        return request.env['eduflow.teacher'].sudo().search(
            [('user_id', '=', request.env.user.id)], limit=1)

    @http.route(['/my/teacher'], type='http', auth='user', website=True)
    def teacher_home(self, **kwargs):
        teacher = self._eduflow_get_teacher()
        if not teacher:
            return request.redirect('/my')
        sessions = request.env['eduflow.timetable.session'].sudo().search(
            [('teacher_id', '=', teacher.id)])
        day_labels = [
            ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
            ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday'),
        ]
        timetable_by_day = {}
        for code, _label in day_labels:
            timetable_by_day[code] = sessions.filtered(lambda s, c=code: s.day == c)
        classrooms = sessions.mapped('classroom_id') | teacher.classroom_ids
        return request.render('eduflow.portal_teacher_home', {
            'teacher': teacher,
            'classrooms': classrooms,
            'day_labels': day_labels,
            'timetable_by_day': timetable_by_day,
        })
