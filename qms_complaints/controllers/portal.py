from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class QmsComplaintPortal(CustomerPortal):
    @http.route(['/my/qms-complaints'], type='http', auth='user', website=True)
    def portal_complaints(self, **kw):
        complaints = request.env['qms.complaint'].search([
            ('partner_id', 'child_of', request.env.user.partner_id.commercial_partner_id.id),
            ('company_id', '=', request.env.company.id),
        ], order='received_at desc')
        return request.render('qms_complaints.portal_my_complaints', {'complaints': complaints})


    @http.route(['/my/qms-complaints/<int:complaint_id>'], type='http', auth='user', website=True)
    def portal_complaint_detail(self, complaint_id, **kw):
        partner = request.env.user.partner_id.commercial_partner_id
        complaint = request.env['qms.complaint'].search([
            ('id', '=', complaint_id),
            ('partner_id', 'child_of', partner.id),
            ('company_id', '=', request.env.company.id),
        ], limit=1)
        if not complaint:
            return request.not_found()
        return request.render('qms_complaints.portal_complaint_detail', {'complaint': complaint})
    @http.route(['/my/qms-complaints/new'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_new_complaint(self, **post):
        if request.httprequest.method == 'POST':
            subject = (post.get('name') or '').strip()
            description = (post.get('description') or '').strip()
            if subject and description:
                request.env['qms.complaint'].create({
                    'name': subject,
                    'partner_id': request.env.user.partner_id.commercial_partner_id.id,
                    'company_id': request.env.company.id,
                    'description': description,
                    'category': post.get('category') or 'service',
                })
                return request.redirect('/my/qms-complaints')
        return request.render('qms_complaints.portal_new_complaint', {})
