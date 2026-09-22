from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestPortalDocument(models.Model):
    _name = 'pest.portal.document'
    _description = 'PestOps Portal Document'
    _order = 'document_date desc, id desc'

    name = fields.Char(required=True, tracking=True)
    document_type = fields.Selection([
        ('service_report', 'Service Report'),
        ('treatment_certificate', 'Treatment Certificate'),
        ('contract', 'Contract Document'),
        ('other', 'Other'),
    ], required=True, default='other', tracking=True)
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', required=True, ondelete='restrict')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='restrict', index=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, index=True)
    site_id = fields.Many2one('pest.site', string='Site', ondelete='restrict', index=True)
    visit_id = fields.Many2one('pest.visit', string='Visit', ondelete='restrict', index=True)
    treatment_id = fields.Many2one('pest.treatment', string='Treatment', ondelete='restrict', index=True)
    service_request_id = fields.Many2one('pest.service.request', string='Service Request', ondelete='set null', index=True)
    document_date = fields.Date(default=fields.Date.context_today, required=True)
    published = fields.Boolean(default=True, tracking=True)
    description = fields.Text()
    download_count = fields.Integer(default=0, readonly=True)

    @api.constrains('site_id', 'visit_id', 'treatment_id', 'partner_id')
    def _check_links(self):
        for record in self:
            if record.site_id and record.site_id.partner_id.commercial_partner_id != record.partner_id.commercial_partner_id:
                raise ValidationError(_('The selected site does not belong to the selected customer.'))
            if record.visit_id:
                if record.visit_id.site_id and record.visit_id.site_id.partner_id.commercial_partner_id != record.partner_id.commercial_partner_id:
                    raise ValidationError(_('The selected visit does not belong to the selected customer.'))
                if record.site_id and record.visit_id.site_id != record.site_id:
                    raise ValidationError(_('The selected visit does not belong to the selected site.'))
            if record.treatment_id:
                visit = record.treatment_id.visit_id
                if visit and visit.site_id.partner_id.commercial_partner_id != record.partner_id.commercial_partner_id:
                    raise ValidationError(_('The selected treatment does not belong to the selected customer.'))

    @api.onchange('site_id')
    def _onchange_site_id(self):
        if self.visit_id and self.site_id and self.visit_id.site_id != self.site_id:
            self.visit_id = False
        if self.site_id:
            self.partner_id = self.site_id.partner_id.commercial_partner_id
            self.company_id = self.site_id.company_id

    @api.onchange('visit_id')
    def _onchange_visit_id(self):
        if self.visit_id:
            self.site_id = self.visit_id.site_id
            self.partner_id = self.visit_id.site_id.partner_id.commercial_partner_id
            self.company_id = self.visit_id.company_id

    @api.onchange('treatment_id')
    def _onchange_treatment_id(self):
        if self.treatment_id:
            self.visit_id = self.treatment_id.visit_id

    def action_toggle_published(self):
        self.write({'published': not self.published})
        return True

    def action_generate_visit_report(self):
        for document in self:
            if not document.visit_id:
                raise UserError(_('A visit is required to generate a service report.'))
            pdf, _ = self.env['ir.actions.report']._render_qweb_pdf(
                'pestops_core.action_report_pest_visit',
                [document.visit_id.id],
            )
            filename = '%s.pdf' % (document.visit_id.name or 'PestOps-Service-Report')
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': __import__('base64').b64encode(pdf),
                'mimetype': 'application/pdf',
                'res_model': 'pest.visit',
                'res_id': document.visit_id.id,
            })
            document.write({
                'name': 'Service Report - %s' % document.visit_id.name,
                'document_type': 'service_report',
                'attachment_id': attachment.id,
                'partner_id': document.visit_id.site_id.partner_id.commercial_partner_id.id,
                'company_id': document.visit_id.company_id.id,
                'site_id': document.visit_id.site_id.id,
                'document_date': fields.Date.context_today(self),
                'published': True,
            })
        return True

    def action_generate_treatment_certificate(self):
        for document in self:
            if not document.treatment_id:
                raise UserError(_('A treatment is required to generate a treatment certificate.'))
            pdf, _ = self.env['ir.actions.report']._render_qweb_pdf(
                'pestops_core.action_report_pest_treatment_certificate',
                [document.treatment_id.id],
            )
            filename = '%s.pdf' % (document.treatment_id.name or 'PestOps-Treatment-Certificate')
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': __import__('base64').b64encode(pdf),
                'mimetype': 'application/pdf',
                'res_model': 'pest.treatment',
                'res_id': document.treatment_id.id,
            })
            visit = document.treatment_id.visit_id
            document.write({
                'name': 'Treatment Certificate - %s' % document.treatment_id.name,
                'document_type': 'treatment_certificate',
                'attachment_id': attachment.id,
                'partner_id': visit.site_id.partner_id.commercial_partner_id.id,
                'company_id': visit.company_id.id,
                'site_id': visit.site_id.id,
                'visit_id': visit.id,
                'treatment_id': document.treatment_id.id,
                'document_date': fields.Date.context_today(self),
                'published': True,
            })
        return True

    def action_download(self):
        self.ensure_one()
        if not self.attachment_id:
            raise UserError(_('No attachment is linked to this document.'))
        self.download_count += 1
        return {
            'type': 'ir.actions.act_url',
            'url': '/my/pestops/document/%s' % self.id,
            'target': 'self',
        }
