from odoo import _, fields, models
from odoo.exceptions import AccessError, UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    fs_cash_review_count = fields.Integer(compute='_compute_fs_cash_review_count')

    def _compute_fs_cash_review_count(self):
        Review = self.env['fs.pos.cash.review']
        data = Review._read_group(
            [('session_id', 'in', self.ids)],
            ['session_id'],
            ['__count'],
        )
        counts = {session.id: count for session, count in data}
        for rec in self:
            rec.fs_cash_review_count = counts.get(rec.id, 0)

    def action_fs_review_cash_closing(self):
        self.ensure_one()
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            raise AccessError(_('Only POS users can open closing reviews.'))
        if self.state not in ('closing_control', 'closed'):
            raise UserError(_('The closing review is available only when the session is in Closing Control or Closed.'))
        review = self.env['fs.pos.cash.review'].create_for_session(self)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fs.pos.cash.review',
            'view_mode': 'form',
            'res_id': review.id,
            'target': 'current',
            'name': _('POS Cash Closing Review'),
        }

    def post_closing_cash_details(self, counted_cash):
        """Store native counted cash first, then enforce the configured approval."""
        result = super().post_closing_cash_details(counted_cash)
        if isinstance(result, dict) and not result.get('successful'):
            return result
        self.ensure_one()
        config = self.env['fs.pos.cash.review.config'].sudo().search(
            [('company_id', '=', self.company_id.id)],
            limit=1,
        )
        if config and config.require_approval_before_close and self.cash_control:
            review = self.env['fs.pos.cash.review'].create_for_session(self)
            if review.state != 'approved':
                return {
                    'successful': False,
                    'message': _('Approve the POS Cash Closing Review before completing this session.'),
                    'redirect': True,
                }
        return result

    def _fs_require_approved_closing_review(self):
        self.ensure_one()
        config = self.env['fs.pos.cash.review.config'].sudo().search(
            [('company_id', '=', self.company_id.id)],
            limit=1,
        )
        if not config or not config.require_approval_before_close or not self.cash_control:
            return True
        review = self.env['fs.pos.cash.review'].search([('session_id', '=', self.id)], limit=1)
        if not review or review.state != 'approved':
            raise UserError(_('Approve the POS Cash Closing Review before closing this session.'))
        return True

    def action_pos_session_closing_control(
        self,
        balancing_account=False,
        amount_to_balance=0,
        bank_payment_method_diffs=None,
    ):
        """Keep Odoo's native transition to Closing Control unchanged."""
        return super().action_pos_session_closing_control(
            balancing_account=balancing_account,
            amount_to_balance=amount_to_balance,
            bank_payment_method_diffs=bank_payment_method_diffs,
        )

    def action_pos_session_close(
        self,
        balancing_account=False,
        amount_to_balance=0,
        bank_payment_method_diffs=None,
    ):
        """Block final posting when the configured cash-closing review is not approved."""
        for session in self.filtered(lambda record: record.cash_control and record.state != 'closed'):
            session._fs_require_approved_closing_review()
        return super().action_pos_session_close(
            balancing_account=balancing_account,
            amount_to_balance=amount_to_balance,
            bank_payment_method_diffs=bank_payment_method_diffs,
        )
