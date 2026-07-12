from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_ids = fields.One2many(
        'contract.contract',
        'partner_id',
        string='Contracts',
    )
    contract_count = fields.Integer(
        string='Contract Count',
        compute='_compute_contract_count',
    )
    active_contract_count = fields.Integer(
        string='Active Contracts',
        compute='_compute_contract_count',
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Company Currency',
        readonly=True,
    )
    total_contract_value = fields.Monetary(
        string='Total Contract Value',
        compute='_compute_contract_count',
        currency_field='company_currency_id',
    )

    @api.depends('contract_ids', 'contract_ids.state', 'contract_ids.amount_total')
    def _compute_contract_count(self):
        for partner in self:
            contracts = partner.contract_ids
            partner.contract_count = len(contracts)
            partner.active_contract_count = len(
                contracts.filtered(lambda c: c.state == 'active')
            )
            company_currency = partner.company_id.currency_id or self.env.company.currency_id
            total = 0.0
            for contract in contracts:
                if contract.currency_id and contract.currency_id != company_currency:
                    total += contract.currency_id._convert(
                        contract.amount_total,
                        company_currency,
                        contract.company_id,
                        contract.date_start or fields.Date.today(),
                    )
                else:
                    total += contract.amount_total or 0.0
            partner.total_contract_value = total

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contracts of %s') % self.name,
            'res_model': 'contract.contract',
            'view_mode': 'list,form,kanban',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
