from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


class PosCashReview(models.Model):
    _name = 'fs.pos.cash.review'
    _description = 'POS Cash Closing Review'
    _inherit = ['mail.thread']
    _check_company_auto = True
    _order = 'create_date desc'

    session_id = fields.Many2one('pos.session', required=True, index=True, ondelete='cascade', check_company=True)
    company_id = fields.Many2one(related='session_id.company_id', store=True, index=True)
    user_id = fields.Many2one('res.users', required=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True, required=True, index=True)
    warning_amount = fields.Float(compute='_compute_thresholds')
    critical_amount = fields.Float(compute='_compute_thresholds')
    total_difference = fields.Monetary(compute='_compute_total', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='session_id.currency_id', store=True)
    line_ids = fields.One2many('fs.pos.cash.review.line', 'review_id', copy=True)
    reason = fields.Text()
    locked = fields.Boolean(compute='_compute_locked')

    _session_unique = models.Constraint(
        'unique (session_id)',
        'Each POS session can only have one closing review.',
    )

    @api.depends('company_id')
    def _compute_thresholds(self):
        Config = self.env['fs.pos.cash.review.config'].sudo()
        configs = Config.search([('company_id', 'in', self.mapped('company_id').ids)])
        config_by_company = {config.company_id.id: config for config in configs}
        for review in self:
            config = config_by_company.get(review.company_id.id)
            review.warning_amount = config.warning_amount if config else 5.0
            review.critical_amount = config.critical_amount if config else 50.0

    @api.depends('line_ids.difference')
    def _compute_total(self):
        for rec in self:
            rec.total_difference = sum(rec.line_ids.mapped('difference'))

    @api.depends('state', 'session_id.state')
    def _compute_locked(self):
        for rec in self:
            rec.locked = rec.state in ('approved', 'rejected') or rec.session_id.state == 'closed'

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_pos_cash_review_internal'):
            raise AccessError(_('POS cash reviews are created by the closing-review workflow.'))
        return super().create(vals_list)

    @api.model
    def _prepare_lines_from_native_close_data(self, session):
        """Build expected/actual values from Odoo's native closing-control source of truth."""
        data = session.get_closing_control_data()
        lines = []
        default_cash = data.get('default_cash_details') or {}
        default_cash_id = default_cash.get('id')
        counted_cash = session.cash_register_balance_end_real
        actual_available = session.state in ('closing_control', 'closed')
        if default_cash_id:
            expected = default_cash.get('amount', 0.0)
            actual = counted_cash if actual_available else expected
            lines.append({
                'payment_method_id': default_cash_id,
                'expected_amount': expected,
                'actual_amount': actual,
            })
        for method_data in data.get('non_cash_payment_methods', []):
            method = self.env['pos.payment.method'].browse(method_data['id']).exists()
            if not method:
                continue
            amount = method_data.get('amount', 0.0)
            lines.append({
                'payment_method_id': method.id,
                'expected_amount': amount,
                'actual_amount': amount,
            })
        return lines

    @api.model
    def create_for_session(self, session):
        """Create or safely refresh the review for a POS session."""
        self._ensure_pos_user()
        existing = self.search([('session_id', '=', session.id)], limit=1)
        if existing:
            if existing.state == 'draft' and session.state != 'closed':
                expected_lines = self._prepare_lines_from_native_close_data(session)
                existing.line_ids.with_context(fs_pos_cash_review_internal=True).unlink()
                existing.with_context(fs_pos_cash_review_internal=True).write({
                    'user_id': session.user_id.id or self.env.user.id,
                    'line_ids': [(0, 0, vals) for vals in expected_lines],
                })
            return existing

        lines = self._prepare_lines_from_native_close_data(session)
        return self.with_context(fs_pos_cash_review_internal=True).create({
            'session_id': session.id,
            'user_id': session.user_id.id or self.env.user.id,
            'line_ids': [(0, 0, vals) for vals in lines],
        })

    def _ensure_pos_user(self):
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            raise AccessError(_('Only POS users can manage closing reviews.'))

    def _check_manager(self):
        if not self.env.user.has_group('point_of_sale.group_pos_manager'):
            raise AccessError(_('Only POS managers can approve or reject a cash closing review.'))

    def write(self, vals):
        protected_fields = {'session_id', 'user_id', 'state', 'warning_amount', 'critical_amount', 'currency_id'}
        if protected_fields.intersection(vals) and not self.env.context.get('fs_cash_review_transition'):
            raise AccessError(_('Review workflow fields can only be changed through the review actions.'))
        locked = self.filtered('locked')
        mutable_fields = set(vals) - {'reason'}
        if locked and mutable_fields:
            raise UserError(_('A closed or approved POS cash review cannot be edited.'))
        return super().write(vals)

    def action_open_justification_wizard(self):
        self.ensure_one()
        self._ensure_pos_user()
        if self.locked:
            raise UserError(_('The closing review is locked.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Enter Variance Justifications'),
            'res_model': 'fs.pos.cash.closing.justification.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_review_id': self.id},
        }

    def action_mark_reviewed(self):
        self._ensure_pos_user()
        for rec in self:
            if rec.locked:
                raise UserError(_('This review is locked and cannot be changed.'))
            if rec.session_id.state == 'closed':
                raise UserError(_('A closed POS session cannot be reviewed.'))
            if any(
                abs(line.difference) > rec.warning_amount and not line.reason
                for line in rec.line_ids
            ):
                raise UserError(
                    _('A reason is required for every payment method above the warning threshold.')
                )
            rec.with_context(fs_cash_review_transition=True).write({'state': 'reviewed'})
        return True

    def action_approve(self):
        self._check_manager()
        for rec in self:
            if rec.session_id.state == 'closed':
                raise UserError(_('A closed POS session cannot be approved or modified.'))
            rec.action_mark_reviewed()
            rec.with_context(fs_cash_review_transition=True).write({'state': 'approved'})
        return True

    def action_reject(self):
        self._check_manager()
        for rec in self:
            if rec.locked:
                raise UserError(_('This review is locked and cannot be changed.'))
            if rec.session_id.state == 'closed':
                raise UserError(_('A closed POS session cannot be rejected.'))
            if not rec.reason or not rec.reason.strip():
                raise UserError(_('A rejection reason is required.'))
            rec.with_context(fs_cash_review_transition=True).write({'state': 'rejected'})
        return True

    def action_open_session(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pos.session',
            'view_mode': 'form',
            'res_id': self.session_id.id,
            'name': _('POS Session'),
        }


class PosCashReviewLine(models.Model):
    _name = 'fs.pos.cash.review.line'
    _description = 'POS Cash Closing Review Line'
    _check_company_auto = True

    review_id = fields.Many2one('fs.pos.cash.review', required=True, ondelete='cascade', check_company=True)
    company_id = fields.Many2one(related='review_id.company_id', store=True, index=True)
    payment_method_id = fields.Many2one('pos.payment.method', required=True, check_company=True)
    expected_amount = fields.Monetary(required=True, currency_field='currency_id', readonly=True)
    actual_amount = fields.Monetary(currency_field='currency_id', readonly=True)
    difference = fields.Monetary(compute='_compute_difference', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='review_id.currency_id', store=True)
    reason = fields.Char()
    severity = fields.Selection([
        ('ok', 'OK'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], compute='_compute_difference', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_pos_cash_review_internal'):
            raise AccessError(_('POS cash review lines are generated by the review workflow.'))
        reviews = self.env['fs.pos.cash.review'].browse(
            [vals.get('review_id') for vals in vals_list if vals.get('review_id')]
        )
        if reviews.filtered('locked'):
            raise UserError(_('A closed or approved POS cash review cannot be edited.'))
        return super().create(vals_list)

    def write(self, vals):
        if {'payment_method_id', 'expected_amount', 'review_id', 'actual_amount'}.intersection(vals):
            raise UserError(_(
                'Payment method, expected amount, actual amount and review ownership are system-controlled.'
            ))
        if 'reason' in vals:
            locked = self.filtered(lambda line: line.review_id.locked)
            if locked:
                raise UserError(_('A closed or approved POS cash review cannot be edited.'))
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get('fs_pos_cash_review_internal'):
            raise AccessError(_('POS cash review lines are generated by the review workflow.'))
        if self.filtered(lambda line: line.review_id.locked):
            raise UserError(_('A closed or approved POS cash review cannot be edited.'))
        return super().unlink()

    @api.depends('expected_amount', 'actual_amount', 'review_id.warning_amount', 'review_id.critical_amount')
    def _compute_difference(self):
        for line in self:
            line.difference = line.actual_amount - line.expected_amount
            amount = abs(line.difference)
            if amount > line.review_id.critical_amount:
                line.severity = 'critical'
            elif amount > line.review_id.warning_amount:
                line.severity = 'warning'
            else:
                line.severity = 'ok'
