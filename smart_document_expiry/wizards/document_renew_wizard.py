# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DocumentRenewWizard(models.TransientModel):
    _name = 'document.renew.wizard'
    _description = 'Document Renewal Wizard'

    document_id = fields.Many2one(
        comodel_name='document.expiry',
        string='Document to Renew',
        required=True,
        readonly=True,
    )
    name             = fields.Char(string='New Document Name', required=True)
    reference        = fields.Char(string='New Reference / Number')
    document_type_id = fields.Many2one('document.expiry.type', string='Document Type', required=True)
    entity_type      = fields.Selection(
        selection=[
            ('person',    'Person / Employee'),
            ('vendor',    'Vendor / Partner'),
            ('vehicle',   'Vehicle'),
            ('equipment', 'Equipment'),
            ('other',     'Other'),
        ],
        string='Entity Type',
        required=True,
        readonly=True,
    )
    person_id        = fields.Many2one('document.person',    string='Person',    readonly=True)
    partner_id       = fields.Many2one('document.partner',   string='Partner',   readonly=True)
    vehicle_id       = fields.Many2one('document.vehicle',   string='Vehicle',   readonly=True)
    equipment_id     = fields.Many2one('document.equipment', string='Equipment', readonly=True)
    other_entity_name = fields.Char(string='Entity Description', readonly=True)

    issue_date   = fields.Date(string='New Issue Date',  default=fields.Date.today)
    expiry_date  = fields.Date(string='New Expiry Date', required=True)

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
    )
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='doc_renew_wizard_attachment_rel',
        column1='wizard_id',
        column2='attachment_id',
        string='New Document Attachments',
    )
    notes = fields.Html(string='Renewal Notes')

    @api.constrains('attachment_ids', 'document_type_id')
    def _check_attachment(self):
        for rec in self:
            if rec.document_type_id.require_renewal_attachment and not rec.attachment_ids:
                raise UserError(_(
                    'Document type "%s" requires at least one attachment when renewing.',
                    rec.document_type_id.name
                ))

    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for rec in self:
            if rec.issue_date and rec.expiry_date and rec.issue_date >= rec.expiry_date:
                raise UserError(_('New Issue Date must be earlier than New Expiry Date.'))

    def action_confirm_renewal(self):
        self.ensure_one()
        old_doc = self.document_id
        old_doc.write({'state': 'renewed'})
        old_doc.message_post(body=_(
            'Document renewed and replaced by <strong>%s</strong>.', self.name
        ))

        new_doc = self.env['document.expiry'].create({
            'name':               self.name,
            'reference':          self.reference,
            'document_type_id':   self.document_type_id.id,
            'entity_type':        self.entity_type,
            'person_id':          self.person_id.id,
            'partner_id':         self.partner_id.id,
            'vehicle_id':         self.vehicle_id.id,
            'equipment_id':       self.equipment_id.id,
            'other_entity_name':  self.other_entity_name,
            'issue_date':         self.issue_date,
            'expiry_date':        self.expiry_date,
            'responsible_id':     self.responsible_id.id,
            'previous_document_id': old_doc.id,
            'notes':              self.notes,
            'company_id':         old_doc.company_id.id,
            'alert_90_sent':      False,
            'alert_30_sent':      False,
            'alert_7_sent':       False,
            'escalation_sent':    False,
        })

        if self.attachment_ids:
            new_doc.attachment_ids = [(4, att.id) for att in self.attachment_ids]

        new_doc.message_post(body=_(
            'Document created as renewal of <strong>%s</strong>.', old_doc.name
        ))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Renewed Document'),
            'res_model': 'document.expiry',
            'res_id': new_doc.id,
            'view_mode': 'form',
            'target': 'current',
        }
