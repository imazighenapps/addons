# -*- coding: utf-8 -*-

from odoo import models, fields,api,_

class MaterialRequest(models.Model):
    _name = 'material.request'
    _description = 'Material Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc'


    name                = fields.Char(string='Number',index=True,readonly=1)
    employee_id         = fields.Many2one('hr.employee',string='Employee',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),required=True,copy=True,)
    department_id       = fields.Many2one('hr.department',string='Department',required=True,copy=True,)
    request_date        = fields.Date(string='Request Date')
    priority            = fields.Selection([('0', 'Low'),('1', 'Medium'),('2', 'High'),('3', 'Very High'),], string='Priority', index=True, default='0')
    receive_date        = fields.Date(string='Received Date', readonly=True, copy=False,)
    company_id          = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required=True,copy=True,)
    request_line_ids    = fields.One2many('material.request.line','request_id',string='Material request line',copy=True,)
    request_approval_ids = fields.One2many('material.request.approval','request_id',string='Approval',copy=True,)
    reason              = fields.Text(string='Reason for Requisitions',required=False,copy=True,)
    delivery_picking_id = fields.Many2one('stock.picking',string='Internal Picking',readonly=True,copy=False,)
    requisiton_responsible_id = fields.Many2one('hr.employee',string='Requisition Responsible',copy=True,)
    employee_confirm_id = fields.Many2one('hr.employee',string='Confirmed by',readonly=True,copy=False,)
    custom_picking_type_id  = fields.Many2one('stock.picking.type',string='Picking Type',copy=False,)
    state                   = fields.Selection([('draft', 'New'),('dept_confirm', 'Waiting Department Approval'),('manager_approve', 'Waiting Manager Approved'),
                              ('approved', 'Approved'),('receive', 'Received'),
                              ('rejected', 'Rejected')],default='draft',track_visibility='onchange',)
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise Warning(_('You can not delete Material Request which is not in draft state.'))
        return super(MaterialRequest, self).unlink()

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('material.request.seq')
        vals.update({'name': name})
        res = super(MaterialRequest, self).create(vals)
        return res                          

    def employee_request_confirm(self):
        for rec in self:
            rec.request_date = fields.Date.today()
            rec.state = 'dept_confirm'

    def dep_request_confirm(self):
        for rec in self:
            line_val = {"request_id"    : rec.id,
                        "state"         :"approved",   
                        "employee_id"   : self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id,
                        "date"          : fields.Date.today(),
                        "reason"        :"",
            }
            self.env['material.request.approval'].create(line_val)
            rec.state = 'manager_approve'

    def manager_request_confirm(self):
            for rec in self:
                line_val = {"request_id"    : rec.id,
                            "state"         :"approved",   
                            "employee_id"   : self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id,
                            "date"          : fields.Date.today(),
                            "reason"        :"",
                }
            self.env['material.request.approval'].create(line_val)
            rec.state = 'approved'

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

    def manager_request_rejected(self):
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
            rec.receive_date = fields.Date.today()
            rec.state = 'receive'


    def create_po(self):
        self.ensure_one()
        vals = []
        for line in self.request_line_ids :
            if line.state != "done" : 
                vals.append((0,0,{"product_id"  :  line.product_id.id,
                                  "description" :  line.description,
                                  "qty"         :  line.qty,
                                  "uom"         :  line.uom.id,
                                  "request_line_id" : line.id,
                                }))       

        ctx = {"default_line_ids" : vals}
        return {
            'name': "Create purchase order",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.po',
            'context' : ctx,
            'target': 'new',
        }

    def create_picking(self):
        self.ensure_one()
        vals = []
        for line in self.request_line_ids :
            if line.state != "done" : 
                vals.append((0,0,{"product_id"  :  line.product_id.id,
                                  "description" :  line.description,
                                  "qty"         :  line.qty,
                                  "uom"         :  line.uom.id,
                                  "request_line_id" : line.id,
                                }))       

        ctx = {"default_line_ids" : vals}
        return {
            'name': "Create Internal transfer",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.picking',
            'context' : ctx,
            'target': 'new',
        }

