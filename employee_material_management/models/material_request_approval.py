# -*- coding: utf-8 -*-

from odoo import models, fields

class MaterialRequestApproval(models.Model):
    _name = 'material.request.approval'
    _description = 'Material Request Approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    request_id     = fields.Many2one('material.request',string='Requisitions',)
    state          = fields.Selection([("approved","Approved"),("rejected","Rejected")],string="State")
    employee_id    = fields.Many2one('hr.employee',string='By',readonly=True,copy=False,)
    department_id  = fields.Many2one('hr.department',string='Department', related="employee_id.department_id")
    date           = fields.Date(string='Date',readonly=True,copy=False,)
    reason         = fields.Char('Reason if rejected')     

