from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestServiceRequest(models.Model):
    _name = 'pest.service.request'
    _description = 'PestOps Customer Service Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.service.request'),
        readonly=True,
        copy=False,
        tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='site_id.company_id',
        store=True,
        index=True,
    )
    site_id = fields.Many2one(
        'pest.site',
        string='Site',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
    )
    visit_id = fields.Many2one(
        'pest.visit',
        string='Related Visit',
        ondelete='set null',
        index=True,
    )
    resservice_id = fields.Many2one(
        'pest.reservice',
        string='Generated Re-Service',
        readonly=True,
        copy=False,
    )
    submitted_by_id = fields.Many2one(
        'res.users',
        string='Submitted By',
        readonly=True,
        default=lambda self: self.env.user,
    )
    request_type = fields.Selection(
        [
            ('reservice', 'Re-Service'),
            ('additional_visit', 'Additional Visit'),
            ('document', 'Document Request'),
            ('other', 'Other'),
        ],
        required=True,
        default='reservice',
        tracking=True,
    )
    priority = fields.Selection(
        [
            ('0', 'Normal'),
            ('1', 'High'),
            ('2', 'Urgent'),
        ],
        default='0',
        required=True,
        tracking=True,
    )
    description = fields.Text(required=True)
    state = fields.Selection(
        [
            ('submitted', 'Submitted'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('rejected', 'Rejected'),
        ],
        default='submitted',
        required=True,
        tracking=True,
    )
    response_notes = fields.Html()
    closed_date = fields.Datetime(readonly=True, copy=False)

    @api.onchange('site_id')
    def _onchange_site_id(self):
        if self.visit_id and self.visit_id.site_id != self.site_id:
            self.visit_id = False

    @api.constrains('site_id', 'partner_id')
    def _check_site_customer(self):
        for record in self:
            if record.site_id and record.site_id.partner_id.commercial_partner_id != record.partner_id.commercial_partner_id:
                raise ValidationError(_('The selected site does not belong to the selected customer.'))

    @api.constrains('visit_id', 'site_id')
    def _check_visit_site(self):
        for record in self:
            if record.visit_id and record.visit_id.site_id != record.site_id:
                raise ValidationError(_('The selected visit does not belong to the selected site.'))

    def action_start(self):
        self.write({'state': 'in_progress'})
        return True

    def action_done(self):
        self.write({
            'state': 'done',
            'closed_date': fields.Datetime.now(),
        })
        return True

    def action_reject(self):
        self.write({
            'state': 'rejected',
            'closed_date': fields.Datetime.now(),
        })
        return True

    def action_reopen(self):
        self.write({'state': 'submitted', 'closed_date': False})
        return True

    def action_create_reservice(self):
        PestReservice = self.env['pest.reservice']
        for request in self.filtered(lambda r: r.request_type == 'reservice' and r.visit_id and not r.resservice_id):
            reservice = PestReservice.create({
                'origin_visit_id': request.visit_id.id,
                'requested_by': request.partner_id.id,
                'reason': 'customer_request',
                'state': 'open',
                'notes': request.description,
            })
            request.resservice_id = reservice.id
        return True
