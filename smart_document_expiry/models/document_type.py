# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DocumentType(models.Model):
    _name = 'document.expiry.type'
    _description = 'Document Expiry Type'
    _order = 'name'

    name = fields.Char(
        string='Document Type',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        help='Short unique code for this document type.',
    )
    entity_type = fields.Selection(
        selection=[
            ('person',    'Person / Employee'),
            ('vendor',    'Vendor / Partner'),
            ('vehicle',   'Vehicle'),
            ('equipment', 'Equipment'),
            ('other',     'Other'),
            ('all',       'All Entities'),
        ],
        string='Applicable To',
        default='all',
        required=True,
    )
    description = fields.Text(string='Description', translate=True)
    color = fields.Integer(string='Color Index', default=0)
    active = fields.Boolean(default=True)
    alert_days_1 = fields.Integer(
        string='First Alert (days before)',
        default=90,
        help='Send first notification this many days before expiry.',
    )
    alert_days_2 = fields.Integer(
        string='Second Alert (days before)',
        default=30,
        help='Send second notification this many days before expiry.',
    )
    alert_days_3 = fields.Integer(
        string='Final Alert (days before)',
        default=7,
        help='Send final notification this many days before expiry.',
    )
    escalation_days = fields.Integer(
        string='Escalation After Expiry (days)',
        default=3,
        help='Days after expiry before escalating to the next manager level.',
    )
    require_renewal_attachment = fields.Boolean(
        string='Require Attachment on Renewal',
        default=True,
        help='Force users to attach a file when renewing this document.',
    )
    document_count = fields.Integer(
        string='Documents',
        compute='_compute_document_count',
    )

    @api.depends('name')
    def _compute_document_count(self):
        DocumentExpiry = self.env['document.expiry']
        for rec in self:
            rec.document_count = DocumentExpiry.search_count(
                [('document_type_id', '=', rec.id)]
            )

    def action_view_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} — Documents',
            'res_model': 'document.expiry',
            'view_mode': 'list,kanban,form',
            'domain': [('document_type_id', '=', self.id)],
            'context': {'default_document_type_id': self.id},
        }
