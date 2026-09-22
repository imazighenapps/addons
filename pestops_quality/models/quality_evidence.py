from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestQualityEvidence(models.Model):
    _name = 'pest.quality.evidence'
    _description = 'PestOps Quality Evidence'
    _order = 'date desc, id desc'

    name = fields.Char(required=True)
    evidence_type = fields.Selection([
        ('photo', 'Photo'),
        ('document', 'Document'),
        ('note', 'Note'),
        ('other', 'Other'),
    ], default='photo', required=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    note = fields.Text()
    file = fields.Binary(attachment=True)
    filename = fields.Char()
    nonconformity_id = fields.Many2one('pest.quality.nonconformity', ondelete='cascade', index=True)
    action_id = fields.Many2one('pest.quality.action', ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', compute='_compute_company', store=True, index=True)

    @api.depends('nonconformity_id.company_id', 'action_id.company_id')
    def _compute_company(self):
        for record in self:
            record.company_id = record.nonconformity_id.company_id or record.action_id.company_id or self.env.company

    @api.constrains('nonconformity_id', 'action_id')
    def _check_parent(self):
        for record in self:
            if bool(record.nonconformity_id) == bool(record.action_id):
                raise ValidationError(_('Evidence must belong to exactly one non-conformity or corrective action.'))
            if record.evidence_type in ('photo', 'document') and not record.file:
                raise ValidationError(_('A photo or document evidence requires a file.'))
            if record.evidence_type == 'note' and not record.note and not record.file:
                raise ValidationError(_('Note evidence requires a note or a file.'))
