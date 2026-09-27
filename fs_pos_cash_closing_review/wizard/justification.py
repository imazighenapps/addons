from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PosCashClosingJustificationWizard(models.TransientModel):
    _name = 'fs.pos.cash.closing.justification.wizard'
    _description = 'POS Cash Closing Justification'

    review_id = fields.Many2one('fs.pos.cash.review', required=True, readonly=True)
    line_ids = fields.One2many('fs.pos.cash.closing.justification.line', 'wizard_id', copy=False)

    @api.model
    def default_get(self, field_list):
        values = super().default_get(field_list)
        review = self.env['fs.pos.cash.review'].browse(
            self.env.context.get('default_review_id') or self.env.context.get('active_id')
        ).exists()
        if not review:
            raise UserError(_('A POS cash closing review is required.'))
        values['review_id'] = review.id
        values['line_ids'] = [(0, 0, {
            'review_line_id': line.id,
            'difference': line.difference,
            'reason': line.reason or '',
        }) for line in review.line_ids.filtered(lambda item: abs(item.difference) > review.warning_amount)]
        return values

    def action_apply(self):
        self.ensure_one()
        if self.review_id.locked:
            raise UserError(_('The closing review is locked.'))
        for line in self.line_ids:
            if abs(line.difference) > self.review_id.warning_amount and not (line.reason or '').strip():
                raise UserError(_('Every variance above the warning threshold requires a reason.'))
            line.review_line_id.write({'reason': (line.reason or '').strip()})
        return {'type': 'ir.actions.act_window_close'}


class PosCashClosingJustificationLine(models.TransientModel):
    _name = 'fs.pos.cash.closing.justification.line'
    _description = 'POS Cash Closing Justification Line'

    wizard_id = fields.Many2one('fs.pos.cash.closing.justification.wizard', required=True, ondelete='cascade')
    review_line_id = fields.Many2one('fs.pos.cash.review.line', required=True, readonly=True)
    payment_method_id = fields.Many2one(related='review_line_id.payment_method_id', readonly=True)
    difference = fields.Monetary(related='review_line_id.difference', readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='wizard_id.review_id.currency_id', readonly=True)
    reason = fields.Char()
