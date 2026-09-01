# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import EduflowTestCommon


@tagged('post_install', '-at_install')
class TestEduflowHrIndependence(EduflowTestCommon):
    """F0.1 -- regression test: the base 'eduflow' module must never
    require 'hr' again. If this test ever fails, someone re-introduced a
    hard dependency and the module would no longer install on a bare
    Odoo 18 Community instance without the Employees app."""

    def test_eduflow_module_does_not_depend_on_hr(self):
        module = self.env['ir.module.module'].search([('name', '=', 'eduflow')], limit=1)
        dependency_names = module.dependencies_id.mapped('name')
        self.assertNotIn('hr', dependency_names,
                          "'eduflow' must not hard-depend on 'hr' (see eduflow_hr_bridge).")

    def test_teacher_has_no_employee_field_without_bridge(self):
        bridge = self.env['ir.module.module'].search(
            [('name', '=', 'eduflow_hr_bridge')], limit=1)
        if bridge and bridge.state == 'installed':
            self.skipTest("eduflow_hr_bridge is installed in this environment")
        self.assertNotIn('employee_id', self.env['eduflow.teacher']._fields)
