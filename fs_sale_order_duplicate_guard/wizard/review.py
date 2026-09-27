from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderDuplicateReviewWizard(models.TransientModel):
    _name = 'fs.sale.order.duplicate.review.wizard'
    _description = 'Review Possible Duplicate Sales Orders'

    sale_order_id = fields.Many2one('sale.order', required=True, readonly=True)
    match_ids = fields.Many2many(
        'fs.sale.order.duplicate.match',
        relation='fs_duplicate_review_match_rel',
        compute='_compute_matches',
        readonly=True,
    )
    decision_note = fields.Text()

    @api.depends('sale_order_id')
    def _compute_matches(self):
        Match = self.env['fs.sale.order.duplicate.match']
        for wizard in self:
            wizard.match_ids = Match.search([
                ('sale_order_id', '=', wizard.sale_order_id.id),
                ('state', '=', 'open'),
            ])

    def action_confirm_anyway(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError(_('No sales order was provided.'))
        if self.decision_note:
            self.sale_order_id.message_post(
                body=_('Duplicate warning reviewed. Decision note: %(note)s', note=self.decision_note)
            )
        self.match_ids.action_ignore(self.decision_note or _('Order confirmed after duplicate review.'))
        return self.sale_order_id.with_context(fs_duplicate_override=True).action_confirm()


    def action_mark_duplicates(self):
        self.ensure_one()
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise UserError(_('Only sales managers can mark duplicate orders.'))
        note = self.decision_note or _('Marked as duplicate after review.')
        self.match_ids.action_mark_duplicate(note)
        self.sale_order_id.message_post(body=note)
        return {'type': 'ir.actions.act_window_close'}

    def action_ignore_matches(self):
        self.ensure_one()
        self.match_ids.action_ignore(self.decision_note)
        return {'type': 'ir.actions.act_window_close'}
