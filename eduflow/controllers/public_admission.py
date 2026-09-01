# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request


class EduflowPublicAdmission(http.Controller):
    """F3.1 -- public pre-registration form accessible from the school's
    public website, without any Odoo login. All writes happen server-side
    under sudo() via eduflow.admission.create_from_public_form, after
    minimal validation + a honeypot anti-spam field."""

    @http.route(['/admissions/apply'], type='http', auth='public',
                website=True, methods=['GET'], sitemap=True)
    def admission_form(self, **kwargs):
        levels = request.env['eduflow.level'].sudo().search([])
        return request.render('eduflow.public_admission_form', {
            'levels': levels,
            'error': kwargs.get('error'),
            'values': {},
        })

    @http.route(['/admissions/apply/submit'], type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def admission_form_submit(self, **post):
        # Honeypot: a hidden field that only a bot would fill in.
        if post.get('website_url'):
            return request.redirect('/admissions/apply')

        required = ['student_name', 'student_firstname', 'level_id', 'parent_name', 'parent_email']
        missing = [f for f in required if not post.get(f)]
        if missing:
            levels = request.env['eduflow.level'].sudo().search([])
            return request.render('eduflow.public_admission_form', {
                'levels': levels,
                'error': _("Please fill in all required fields."),
                'values': post,
            })

        try:
            level_id = int(post.get('level_id'))
        except (TypeError, ValueError):
            level_id = False

        admission = request.env['eduflow.admission'].sudo().create_from_public_form({
            'student_name': post.get('student_name'),
            'student_firstname': post.get('student_firstname'),
            'student_birth_date': post.get('student_birth_date'),
            'level_id': level_id,
            'parent_name': post.get('parent_name'),
            'parent_email': post.get('parent_email'),
            'parent_phone': post.get('parent_phone'),
            'parent_relation': post.get('parent_relation', 'guardian'),
            'notes': post.get('notes'),
        })
        return request.render('eduflow.public_admission_thanks', {'admission': admission})
