# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError

def _check_dashboard_access():
    if not (request.env.user.has_group('eduflow.group_eduflow_direction')
            or request.env.user.has_group('eduflow.group_eduflow_admin')
            or request.env.user.has_group('eduflow.group_eduflow_administration')):
        raise AccessError(_("Access denied: Dashboard reserved to management (Direction/Administration)."))

class DashboardEducationController(http.Controller):

    @http.route('/dashboard/education/data', type='json', auth='user')
    def get_dashboard_data(self, year_id=None):
        _check_dashboard_access()
        return request.env['dashboard.education'].get_dashboard_data(year_id=int(year_id) if year_id else None)

    @http.route('/dashboard/education/enrollment', type='json', auth='user')
    def get_enrollment(self, year_id=None):
        _check_dashboard_access()
        return request.env['dashboard.education'].get_enrollment_kpis(year_id=int(year_id) if year_id else None)

    @http.route('/dashboard/education/finance', type='json', auth='user')
    def get_finance(self, year_id=None):
        _check_dashboard_access()
        return request.env['dashboard.education'].get_finance_kpis(year_id=int(year_id) if year_id else None)

    @http.route('/dashboard/education/attendance', type='json', auth='user')
    def get_attendance(self, year_id=None):
        _check_dashboard_access()
        return request.env['dashboard.education'].get_attendance_kpis(year_id=int(year_id) if year_id else None)
