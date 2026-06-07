# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DocumentEquipment(models.Model):
    """Standalone equipment model — no dependency on any external module."""
    _name = 'document.equipment'
    _description = 'Equipment'
    _order = 'name'

    name = fields.Char(string='Equipment Name', required=True)
    reference = fields.Char(string='Internal Reference')
    category = fields.Char(string='Category')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')

    document_expiry_ids = fields.One2many(
        comodel_name='document.expiry',
        inverse_name='equipment_id',
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
    compliance_score = fields.Float(
        string='Compliance (%)',
        compute='_compute_document_expiry_count',
    )

    @api.depends('document_expiry_ids', 'document_expiry_ids.state')
    def _compute_document_expiry_count(self):
        for eq in self:
            docs = eq.document_expiry_ids.filtered(lambda d: d.state != 'archived')
            total = len(docs)
            expired = docs.filtered(lambda d: d.state == 'expired')
            valid   = docs.filtered(lambda d: d.state == 'valid')
            eq.document_expiry_count  = total
            eq.document_expired_count = len(expired)
            eq.compliance_score = round(len(valid) / total * 100, 1) if total else 100.0

    def action_view_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} — Documents',
            'res_model': 'document.expiry',
            'view_mode': 'list,kanban,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {
                'default_equipment_id': self.id,
                'default_entity_type': 'equipment',
            },
        }
