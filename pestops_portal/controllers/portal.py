import re

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PestOpsCustomerPortal(CustomerPortal):
    """Portal routes with explicit commercial-partner ownership checks."""

    def _commercial_partner(self):
        return request.env.user.partner_id.commercial_partner_id

    def _site_domain(self):
        return [('partner_id', 'child_of', [self._commercial_partner().id])]

    def _visit_domain(self):
        return [('site_id.partner_id', 'child_of', [self._commercial_partner().id])]

    def _request_domain(self):
        return [('partner_id', 'child_of', [self._commercial_partner().id])]

    def _document_domain(self):
        return [
            ('published', '=', True),
            ('partner_id', 'child_of', [self._commercial_partner().id]),
        ]

    def _get_document(self, document_id):
        document = request.env['pest.portal.document'].sudo().search(
            self._document_domain() + [('id', '=', document_id)],
            limit=1,
        )
        if not document:
            raise MissingError(_('Document not found.'))
        return document

    def _get_site(self, site_id):
        site = request.env['pest.site'].sudo().search(
            self._site_domain() + [('id', '=', site_id)],
            limit=1,
        )
        if not site:
            raise MissingError(_('Site not found.'))
        return site

    def _get_visit(self, visit_id):
        visit = request.env['pest.visit'].sudo().search(
            self._visit_domain() + [('id', '=', visit_id)],
            limit=1,
        )
        if not visit:
            raise MissingError(_('Visit not found.'))
        return visit

    def _get_request(self, request_id):
        service_request = request.env['pest.service.request'].sudo().search(
            self._request_domain() + [('id', '=', request_id)],
            limit=1,
        )
        if not service_request:
            raise MissingError(_('Service request not found.'))
        return service_request

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        Site = request.env['pest.site'].sudo()
        Visit = request.env['pest.visit'].sudo()
        ServiceRequest = request.env['pest.service.request'].sudo()
        Document = request.env['pest.portal.document'].sudo()
        if 'pest_site_count' in counters:
            values['pest_site_count'] = Site.search_count(self._site_domain())
        if 'pest_visit_count' in counters:
            values['pest_visit_count'] = Visit.search_count(self._visit_domain())
        if 'pest_request_count' in counters:
            values['pest_request_count'] = ServiceRequest.search_count(self._request_domain())
        if 'pest_document_count' in counters:
            values['pest_document_count'] = Document.search_count(self._document_domain())
        return values

    @http.route('/my/pestops', type='http', auth='user', website=True)
    def portal_pestops_dashboard(self, **kw):
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops',
            'site_count': request.env['pest.site'].sudo().search_count(self._site_domain()),
            'visit_count': request.env['pest.visit'].sudo().search_count(self._visit_domain()),
            'request_count': request.env['pest.service.request'].sudo().search_count(self._request_domain()),
            'document_count': request.env['pest.portal.document'].sudo().search_count(self._document_domain()),
            'recent_documents': request.env['pest.portal.document'].sudo().search(
                self._document_domain(), order='document_date desc, id desc', limit=6,
            ),
            'upcoming_visits': request.env['pest.visit'].sudo().search(
                self._visit_domain() + [
                    ('scheduled_start', '!=', False),
                    ('state', 'in', ['draft', 'scheduled', 'in_progress']),
                ],
                order='scheduled_start asc, id asc',
                limit=8,
            ),
        })
        return request.render('pestops_portal.portal_pestops_dashboard', values)

    @http.route('/my/pestops/sites', type='http', auth='user', website=True)
    def portal_pestops_sites(self, **kw):
        sites = request.env['pest.site'].sudo().search(
            self._site_domain(),
            order='name asc, id asc',
        )
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops_sites',
            'sites': sites,
        })
        return request.render('pestops_portal.portal_pestops_sites', values)

    @http.route('/my/pestops/site/<int:site_id>', type='http', auth='user', website=True)
    def portal_pestops_site(self, site_id, **kw):
        try:
            site = self._get_site(site_id)
        except (MissingError, AccessError):
            return request.not_found()
        visits = request.env['pest.visit'].sudo().search(
            self._visit_domain() + [('site_id', '=', site.id)],
            order='scheduled_start desc, id desc',
            limit=20,
        )
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops_site',
            'site': site,
            'visits': visits,
        })
        return request.render('pestops_portal.portal_pestops_site', values)

    @http.route('/my/pestops/visits', type='http', auth='user', website=True)
    def portal_pestops_visits(self, **kw):
        visits = request.env['pest.visit'].sudo().search(
            self._visit_domain(),
            order='scheduled_start desc, id desc',
            limit=100,
        )
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops_visits',
            'visits': visits,
        })
        return request.render('pestops_portal.portal_pestops_visits', values)

    @http.route('/my/pestops/visit/<int:visit_id>', type='http', auth='user', website=True)
    def portal_pestops_visit(self, visit_id, **kw):
        try:
            visit = self._get_visit(visit_id)
        except (MissingError, AccessError):
            return request.not_found()
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops_visit',
            'visit': visit,
        })
        return request.render('pestops_portal.portal_pestops_visit', values)

    def _render_pdf_report(self, report_xmlid, record, filename_prefix):
        try:
            report = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                report_xmlid,
                [record.id],
            )[0]
        except Exception:
            raise MissingError(_('The requested document could not be generated.'))
        safe_name = re.sub(r'[^A-Za-z0-9._-]+', '-', record.display_name or str(record.id)).strip('-')
        filename = f'{filename_prefix}-{safe_name}.pdf'
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', str(len(report))),
            ('Content-Disposition', f'attachment; filename="{filename}"'),
        ]
        return request.make_response(report, headers=headers)

    @http.route('/my/pestops/report/visit/<int:visit_id>', type='http', auth='user', website=True)
    def portal_pestops_visit_report(self, visit_id, **kw):
        try:
            visit = self._get_visit(visit_id)
            return self._render_pdf_report(
                'pestops_core.action_report_pest_visit',
                visit,
                'PestOps-Service-Report',
            )
        except (MissingError, AccessError):
            return request.not_found()

    @http.route('/my/pestops/report/treatment/<int:treatment_id>', type='http', auth='user', website=True)
    def portal_pestops_treatment_report(self, treatment_id, **kw):
        treatment = request.env['pest.treatment'].sudo().search([
            ('id', '=', treatment_id),
            ('visit_id.site_id.partner_id', 'child_of', [self._commercial_partner().id]),
        ], limit=1)
        if not treatment:
            return request.not_found()
        try:
            return self._render_pdf_report(
                'pestops_core.action_report_pest_treatment_certificate',
                treatment,
                'PestOps-Treatment-Certificate',
            )
        except (MissingError, AccessError):
            return request.not_found()

    @http.route('/my/pestops/documents', type='http', auth='user', website=True)
    def portal_pestops_documents(self, **kw):
        documents = request.env['pest.portal.document'].sudo().search(
            self._document_domain(),
            order='document_date desc, id desc',
            limit=100,
        )
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops_documents',
            'documents': documents,
        })
        return request.render('pestops_portal.portal_pestops_documents', values)

    @http.route('/my/pestops/document/<int:document_id>', type='http', auth='user', website=True)
    def portal_pestops_document_download(self, document_id, **kw):
        try:
            document = self._get_document(document_id)
        except (MissingError, AccessError):
            return request.not_found()
        attachment = document.attachment_id
        if not attachment or attachment.type != 'binary' or not attachment.datas:
            return request.not_found()
        import base64
        data = base64.b64decode(attachment.datas)
        document.sudo().write({'download_count': document.download_count + 1})
        filename = attachment.name or document.name or 'PestOps-document'
        headers = [
            ('Content-Type', attachment.mimetype or 'application/octet-stream'),
            ('Content-Length', str(len(data))),
            ('Content-Disposition', 'attachment; filename="%s"' % filename.replace('"', '')),
        ]
        return request.make_response(data, headers=headers)

    @http.route('/my/pestops/requests', type='http', auth='user', website=True)
    def portal_pestops_requests(self, **kw):
        service_requests = request.env['pest.service.request'].sudo().search(
            self._request_domain(),
            order='create_date desc, id desc',
            limit=100,
        )
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops_requests',
            'service_requests': service_requests,
        })
        return request.render('pestops_portal.portal_pestops_requests', values)

    @http.route('/my/pestops/request', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_pestops_request_create(self, **post):
        Site = request.env['pest.site'].sudo()
        Visit = request.env['pest.visit'].sudo()
        sites = Site.search(self._site_domain(), order='name asc, id asc')
        visits = Visit.search(self._visit_domain(), order='scheduled_start desc, id desc', limit=100)
        errors = []

        if request.httprequest.method == 'POST':
            try:
                site_id = int(post.get('site_id', '0'))
            except (TypeError, ValueError):
                site_id = 0
            try:
                visit_id = int(post.get('visit_id', '0'))
            except (TypeError, ValueError):
                visit_id = 0

            site = Site.search(self._site_domain() + [('id', '=', site_id)], limit=1) if site_id else Site.browse()
            visit = Visit.search(self._visit_domain() + [('id', '=', visit_id)], limit=1) if visit_id else Visit.browse()

            if not site:
                errors.append(_('Please select a valid site.'))
            if visit and visit.site_id != site:
                errors.append(_('The selected visit does not belong to the selected site.'))
            if not post.get('description', '').strip():
                errors.append(_('Please describe your request.'))

            if not errors:
                service_request = request.env['pest.service.request'].sudo().create({
                    'partner_id': self._commercial_partner().id,
                    'company_id': site.company_id.id or request.env.company.id,
                    'site_id': site.id,
                    'visit_id': visit.id if visit else False,
                    'request_type': post.get('request_type') or 'reservice',
                    'priority': post.get('priority') or '0',
                    'description': post.get('description', '').strip(),
                    'submitted_by_id': request.env.user.id,
                    'state': 'submitted',
                })
                if service_request.request_type == 'reservice' and service_request.visit_id:
                    service_request.action_create_reservice()
                service_request.message_post(body=_('Customer portal request submitted.'))
                return request.redirect(f'/my/pestops/request/{service_request.id}')

        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops_request_new',
            'sites': sites,
            'visits': visits,
            'errors': errors,
            'form': post,
        })
        return request.render('pestops_portal.portal_pestops_request_form', values)

    @http.route('/my/pestops/request/<int:request_id>', type='http', auth='user', website=True)
    def portal_pestops_request(self, request_id, **kw):
        try:
            service_request = self._get_request(request_id)
        except (MissingError, AccessError):
            return request.not_found()
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'pestops_request',
            'service_request': service_request,
        })
        return request.render('pestops_portal.portal_pestops_request', values)
