from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ContractClauseInsertWizard(models.TransientModel):
    _name = 'contract.clause.insert.wizard'
    _description = 'Insert Clauses Into Contract Wizard'

    contract_id = fields.Many2one(
        'contract.contract', string='Contract', required=True, readonly=True,
    )
    clause_ids = fields.Many2many(
        'contract.clause', string='Clauses to Insert',
        domain="['|', ('applicable_to', '=', 'all'), "
               "('applicable_to', '=', contract_type_context)]",
    )
    contract_type_context = fields.Char(
        compute='_compute_contract_type_context',
    )

    @api.depends('contract_id')
    def _compute_contract_type_context(self):
        for rec in self:
            ctype = rec.contract_id.contract_type
            rec.contract_type_context = 'customer' if ctype in (
                'customer', 'service', 'partnership', 'nda', 'employment',
                'lease', 'other',
            ) else 'supplier'

    def action_insert_clauses(self):
        self.ensure_one()
        if not self.clause_ids:
            raise UserError(_("Select at least one clause to insert."))

        existing = self.contract_id.description or ''
        blocks = [existing] if existing.strip() else []
        for clause in self.clause_ids.sorted(key=lambda c: (c.category, c.sequence)):
            blocks.append(
                '<h4>%s</h4>%s' % (clause.name, clause.content or '')
            )
        self.contract_id.description = ''.join(blocks)

        self.contract_id.message_post(
            body=_('Clauses inserted: %s') % ', '.join(self.clause_ids.mapped('name')),
            message_type='comment', subtype_xmlid='mail.mt_note',
        )
        return {'type': 'ir.actions.act_window_close'}
