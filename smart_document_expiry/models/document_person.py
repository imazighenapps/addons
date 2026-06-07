# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DocumentPerson(models.Model):
    """Standalone person/employee model — no dependency on hr module."""
    _name = 'document.person'
    _description = 'Person'
    _order = 'name'

    name = fields.Char(string='Full Name', required=True)
    job_title = fields.Char(string='Job Title / Position')
    department = fields.Char(string='Department')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')

    document_expiry_ids = fields.One2many(
        comodel_name='document.expiry',
        inverse_name='person_id',
        string='Documents',
        domain=[('state', '!=', 'archived')],
    )
    document_expiry_count = fields.Integer(
        string='Documents',
        compute='_compute_document_expiry_count',
    )
    document_expired_count = fields.Integer(
        string='Expired',
        compute='_compute_document_expiry_count',
    )
    document_expiring_count = fields.Integer(
        string='Expiring Soon',
        compute='_compute_document_expiry_count',
    )
    compliance_score = fields.Float(
        string='Compliance (%)',
        compute='_compute_document_expiry_count',
    )

    @api.depends('document_expiry_ids', 'document_expiry_ids.state')
    def _compute_document_expiry_count(self):
        for rec in self:
            docs = rec.document_expiry_ids.filtered(lambda d: d.state != 'archived')
            total = len(docs)
            rec.document_expiry_count   = total
            rec.document_expired_count  = len(docs.filtered(lambda d: d.state == 'expired'))
            rec.document_expiring_count = len(docs.filtered(lambda d: d.state == 'expiring_soon'))
            valid = len(docs.filtered(lambda d: d.state == 'valid'))
            rec.compliance_score = round(valid / total * 100, 1) if total else 100.0

    def action_view_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} — Documents',
            'res_model': 'document.expiry',
            'view_mode': 'list,kanban,form',
            'domain': [('person_id', '=', self.id)],
            'context': {
                'default_person_id': self.id,
                'default_entity_type': 'person',
            },
        }
