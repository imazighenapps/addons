from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pestops_contract_id = fields.Many2one(
        'pest.contract',
        string='PestOps Contract',
        readonly=True,
        copy=False,
    )
    pestops_enabled = fields.Boolean(
        string='PestOps Service',
        default=False,
    )
    pestops_start_date = fields.Date(
        string='Service Start',
    )
    pestops_end_date = fields.Date(
        string='Service End',
    )
    pestops_frequency_type = fields.Selection(
        [
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
        ],
        string='Visit Frequency',
        default='weeks',
    )
    pestops_frequency_number = fields.Integer(
        string='Frequency',
        default=2,
    )
    pestops_visit_duration_minutes = fields.Integer(
        string='Visit Duration',
        default=60,
    )
    pestops_technician_id = fields.Many2one(
        'res.users',
        string='Default Technician',
    )
    pestops_site_ids = fields.Many2many(
        'pest.site',
        'sale_order_pest_site_rel',
        'order_id',
        'site_id',
        string='Service Sites',
        domain="[('partner_id', '=', partner_id)]",
    )
    pestops_billing_frequency = fields.Selection(
        [
            ('once', 'One-off'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annual', 'Annual'),
            ('per_visit', 'Per Visit'),
        ],
        string='Billing Frequency',
        default='monthly',
    )

    def action_create_pestops_contract(self):
        self.ensure_one()
        if not self.pestops_enabled:
            raise UserError(_('Enable "PestOps Service" first.'))
        if not self.pestops_site_ids:
            raise UserError(_('Select at least one PestOps service site.'))
        if self.pestops_contract_id:
            return self.action_open_pestops_contract()

        wizard = self.env['pestops.sale.create.contract.wizard'].create({
            'sale_order_id': self.id,
            'partner_id': self.partner_id.id,
            'start_date': self.pestops_start_date or fields.Date.context_today(self),
            'end_date': self.pestops_end_date,
            'frequency_type': self.pestops_frequency_type or 'weeks',
            'frequency_number': self.pestops_frequency_number or 2,
            'visit_duration_minutes': self.pestops_visit_duration_minutes or 60,
            'technician_id': self.pestops_technician_id.id or False,
            'billing_frequency': self.pestops_billing_frequency or 'monthly',
            'site_ids': [(6, 0, self.pestops_site_ids.ids)],
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create PestOps Contract'),
            'res_model': 'pestops.sale.create.contract.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_open_pestops_contract(self):
        self.ensure_one()
        if not self.pestops_contract_id:
            raise UserError(_('No PestOps contract is linked to this order.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('PestOps Contract'),
            'res_model': 'pest.contract',
            'view_mode': 'form',
            'res_id': self.pestops_contract_id.id,
        }

    def action_confirm(self):
        result = super().action_confirm()
        for order in self:
            contract = order.pestops_contract_id
            if contract and contract.state in ('draft', 'to_renew'):
                contract.action_confirm()
        return result
