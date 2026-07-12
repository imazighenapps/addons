from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class ContractPortal(CustomerPortal):
    """Portal controller letting partners view their own contracts."""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'contract_count' in counters:
            partner = request.env.user.partner_id
            values['contract_count'] = request.env['contract.contract'].search_count([
                ('partner_id', 'in', [partner.id, partner.commercial_partner_id.id]),
                ('state', 'not in', ['cancelled', 'draft']),
            ])
        return values

    @http.route([
        '/my/contracts',
        '/my/contracts/page/<int:page>',
    ], type='http', auth='user', website=True)
    def portal_my_contracts(self, page=1, sortby=None, filterby=None, **kw):
        partner = request.env.user.partner_id
        Contract = request.env['contract.contract']

        domain = [
            ('partner_id', 'in', [partner.id, partner.commercial_partner_id.id]),
            ('state', 'not in', ['cancelled', 'draft']),
        ]

        searchbar_sortings = {
            'date_end': {'label': _("Expiry Date"), 'order': 'date_end asc'},
            'name': {'label': _('Reference'), 'order': 'name asc'},
            'amount': {'label': _('Amount'), 'order': 'amount_total desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'active': {'label': _('Active'), 'domain': [('state', '=', 'active')]},
            'expiring': {'label': _('Expiring Soon'), 'domain': [('is_near_expiry', '=', True)]},
            'expired': {'label': _('Expired'), 'domain': [('state', '=', 'expired')]},
        }

        sortby = sortby or 'date_end'
        filterby = filterby or 'all'
        order = searchbar_sortings[sortby]['order']
        domain += searchbar_filters[filterby]['domain']

        contract_count = Contract.search_count(domain)
        pager = portal_pager(
            url='/my/contracts',
            url_args={'sortby': sortby, 'filterby': filterby},
            total=contract_count,
            page=page,
            step=10,
        )
        contracts = Contract.search(domain, order=order,
                                    limit=10, offset=pager['offset'])

        return request.render('smart_contract_lifecycle.portal_my_contracts', {
            'contracts': contracts,
            'page_name': 'contract',
            'pager': pager,
            'default_url': '/my/contracts',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })

    @http.route(['/my/contracts/<int:contract_id>'],
                type='http', auth='user', website=True)
    def portal_contract_detail(self, contract_id, **kw):
        try:
            contract = self._document_check_access(
                'contract.contract', contract_id,
            )
        except (AccessError, MissingError):
            return request.redirect('/my/contracts')

        return request.render('smart_contract_lifecycle.portal_contract_detail', {
            'contract': contract,
            'page_name': 'contract',
        })
