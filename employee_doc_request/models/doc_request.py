# -*- coding: utf-8 -*-

from odoo import models, fields,api,_

class DocRequest(models.Model):
    _name = 'doc.request'
    _description = 'Document Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc'


    name                = fields.Char(string='Number',index=True,readonly=1)
    employee_id         = fields.Many2one('hr.employee',string='Employee',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),required=True,copy=True,)
    department_id       = fields.Many2one('hr.department',string='Department',required=True,copy=True,default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).department_id)
    emp_request_to      = fields.Many2one('hr.employee',string='Employee Request to',required=True,copy=True,)
    dep_request_to      = fields.Many2one('hr.department',string='Department Request to',required=True,copy=True,)


    request_date        = fields.Date(string='Request Date')
    received_date        = fields.Date(string='Received Date')
    rejected_date       = fields.Date(string='Rejected Date')
    priority            = fields.Selection([('0', 'Low'),('1', 'Medium'),('2', 'High'),('3', 'Very High'),], string='Priority', index=True, default='0')
    state               = fields.Selection([('draft', 'New'),('dept_confirm', 'Waiting Approval'),
                                            ('done', 'Done'),('received', 'Received'),
                                            ('rejected', 'Rejected')],default='draft',track_visibility='onchange',)
    document_type_id    = fields.Many2one('doc.type',string="Document", required=True, domain ="['|',('visibility_type','=','all_department'),('department_id','=',department_id)]" )#,('department_id','=',employee_id.department_id.id)
    receiving_mode      = fields.Selection([('attachment','Attachment'),('hand_to_hand','Hand to hand')])  
                 
    file                = fields.Binary('File', attachment=False)
    filename            = fields.Char('File Name')
    rejected_reason     = fields.Char('Rejected reason')
    company_id          = fields.Many2one('res.company', string='Company', required=True,default=lambda self: self.env.company)
    
    @api.onchange('emp_request_to')
    def _onchange_emp_request_to(self):
        if self.emp_request_to:
            self.dep_request_to =  self.emp_request_to.department_id.id

    
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise Warning(_('You can not delete Document Request which is not in draft state.'))
        return super(DocRequest, self).unlink()

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('doc.request.seq')
        vals.update({'name': name})
        res = super(DocRequest, self).create(vals)
        return res                          


    def employee_request_confirm(self):
        for rec in self:
            rec.request_date = fields.Date.today()
            rec.state = 'dept_confirm'

    def dep_request_confirm(self):
        self.state = 'done'


    def dep_request_rejected(self):
        self.ensure_one()
        return {
            'name': "Rejected reason",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'rejected.reason',
            'target': 'new',
        }

   

    def action_received(self):
        for rec in self:
            rec.received_date = fields.Date.today()
            rec.state = 'received'


    