from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _name = 'contract.contract'
    _description = 'Contract'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date_start desc, id desc'
    _rec_name = 'name'

    _sql_constraints = [
        (
            'name_company_unique',
            'UNIQUE(name, company_id)',
            'The contract reference must be unique per company.',
        ),
    ]

    name = fields.Char(
        string='Contract Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        tracking=True,
    )
    title = fields.Char(string='Contract Title', required=True, tracking=True)
    contract_type = fields.Selection([
        ('customer', 'Customer Contract'),
        ('supplier', 'Vendor Contract'),
        ('partnership', 'Partnership'),
        ('nda', 'NDA / Confidentiality'),
        ('employment', 'Employment Contract'),
        ('lease', 'Lease / Rental'),
        ('service', 'Service Agreement'),
        ('other', 'Other'),
    ], string='Contract Type', required=True, default='customer', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('negotiation', 'Negotiation'),
        ('pending_approval', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('renewed', 'Renewed'),
    ], string='Status', default='draft', tracking=True, required=True)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Critical'),
    ], string='Priority', default='0')

    version = fields.Integer(string='Version', default=1, readonly=True)
    active = fields.Boolean(default=True)

    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True, tracking=True,
        domain="[('active', '=', True)]",
    )
    partner_contact_id = fields.Many2one(
        'res.partner', string='Partner Contact',
        domain="[('parent_id', '=', partner_id)]",
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company, required=True,
    )
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        default=lambda self: self.env.user, tracking=True,
    )
    approver_id = fields.Many2one('res.users', string='Approver', tracking=True)

    approval_line_ids = fields.One2many(
        'contract.approval.line', 'contract_id', string='Approval Steps',
    )
    current_approval_line_id = fields.Many2one(
        'contract.approval.line', string='Current Step',
        compute='_compute_current_approval_line',
    )
    approval_progress = fields.Char(
        string='Approval Progress', compute='_compute_current_approval_line',
    )
    can_user_approve = fields.Boolean(
        string='Current User Can Approve',
        compute='_compute_can_user_approve',
    )

    team_ids = fields.Many2many(
        'res.users', 'contract_user_rel', 'contract_id', 'user_id',
        string='Contract Team',
    )

    date_start = fields.Date(
        string='Start Date', required=True, tracking=True,
        default=fields.Date.today,
    )
    date_end = fields.Date(string='End Date', tracking=True)
    date_signed = fields.Date(string='Signature Date', tracking=True)
    date_notice = fields.Date(
        string='Notice Date',
        compute='_compute_date_notice', store=True,
        help='Deadline to notify renewal or termination.',
    )
    notice_days = fields.Integer(string='Notice Period (days)', default=30)

    duration_type = fields.Selection([
        ('fixed', 'Fixed Term'),
        ('indefinite', 'Indefinite Term'),
        ('recurring', 'Recurring / Subscription'),
    ], string='Duration Type', default='fixed', required=True)

    renewal_type = fields.Selection([
        ('none', 'No Renewal'),
        ('manual', 'Manual Renewal'),
        ('automatic', 'Automatic Renewal'),
    ], string='Renewal', default='manual')

    renewal_duration = fields.Integer(string='Renewal Duration', default=12)
    renewal_duration_unit = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years'),
    ], string='Unit', default='months')

    parent_contract_id = fields.Many2one(
        'contract.contract', string='Parent Contract (Renewal)', readonly=True,
    )
    child_contract_ids = fields.One2many(
        'contract.contract', 'parent_contract_id', string='Renewals',
    )
    renewal_count = fields.Integer(string='Renewal Count', compute='_compute_renewal_count')

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    amount_total = fields.Monetary(
        string='Total Contract Value', currency_field='currency_id', tracking=True,
    )
    amount_invoiced = fields.Monetary(
        string='Amount Invoiced', currency_field='currency_id',
        compute='_compute_amount_invoiced', store=False,
    )
    amount_remaining = fields.Monetary(
        string='Remaining to Invoice', currency_field='currency_id',
        compute='_compute_amount_invoiced', store=False,
    )
    payment_terms_id = fields.Many2one('account.payment.term', string='Payment Terms')
    billing_frequency = fields.Selection([
        ('one_time', 'One-time Payment'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-annual'),
        ('annual', 'Annual'),
    ], string='Billing Frequency', default='one_time')

    description = fields.Html(string='Description / Purpose')
    internal_notes = fields.Html(string='Internal Notes')
    template_id = fields.Many2one('contract.template', string='Contract Template')
    tag_ids = fields.Many2many('contract.tag', string='Tags')

    amendment_ids = fields.One2many('contract.amendment', 'contract_id', string='Amendments')
    amendment_count = fields.Integer(string='Amendment Count', compute='_compute_amendment_count')
    milestone_ids = fields.One2many('contract.milestone', 'contract_id', string='Milestones / Deliverables')

    sale_order_ids = fields.Many2many(
        'sale.order', 'contract_sale_order_rel', 'contract_id', 'sale_order_id',
        string='Related Quotations / Orders',
        domain="[('partner_id', 'child_of', partner_id)]",
    )
    sale_order_count = fields.Integer(string='Quotations/Sales', compute='_compute_order_counts')
    purchase_order_ids = fields.Many2many(
        'purchase.order', 'contract_purchase_order_rel', 'contract_id', 'purchase_order_id',
        string='Related Vendor Orders',
        domain="[('partner_id', 'child_of', partner_id)]",
    )
    purchase_order_count = fields.Integer(string='Purchases', compute='_compute_order_counts')

    document_count = fields.Integer(string='Documents', compute='_compute_document_count')

    days_remaining = fields.Integer(
        string='Days Remaining', compute='_compute_days_remaining', store=True,
    )
    progress = fields.Float(string='Progress (%)', compute='_compute_progress')
    is_near_expiry = fields.Boolean(
        string='Near Expiry', compute='_compute_is_near_expiry', store=True,
    )
    is_expired = fields.Boolean(
        string='Expired', compute='_compute_is_expired', store=True,
    )
    health_status = fields.Selection([
        ('green', 'Healthy'),
        ('orange', 'Needs Attention'),
        ('red', 'Critical'),
    ], string='Contract Health', compute='_compute_health_status', store=True)

    mrr = fields.Monetary(
        string='Monthly Recurring Revenue (MRR)',
        compute='_compute_mrr', store=True, currency_field='currency_id',
        help="Contract value normalized to a monthly basis, used for MRR/ARR "
             "calculation. Zero for non-recurring contracts (one-time billing).",
    )

    risk_score = fields.Integer(
        string='Risk Score', compute='_compute_risk_score', store=True,
        help="0 = minimal risk, 100 = maximal risk. Calculated from weighted "
             "criteria: missing termination clause, high amount without "
             "approval, signature delay, late milestones, partner history.",
    )
    risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Risk Level', compute='_compute_risk_score', store=True)
    risk_factors = fields.Text(
        string='Risk Factors', compute='_compute_risk_score',
        help="Details of the factors contributing to the risk score.",
    )

    signed_by_us = fields.Boolean(string='Signed by Our Company', tracking=True)
    signed_by_partner = fields.Boolean(string='Signed by Partner', tracking=True)
    signature_our = fields.Binary(string='Signature (Our Company)')
    signature_partner = fields.Binary(string='Signature (Partner)')

    @api.depends('date_end', 'notice_days')
    def _compute_date_notice(self):
        for rec in self:
            if rec.date_end and rec.notice_days:
                rec.date_notice = rec.date_end - relativedelta(days=rec.notice_days)
            else:
                rec.date_notice = False

    @api.depends('date_end')
    def _compute_days_remaining(self):
        today = date.today()
        for rec in self:
            rec.days_remaining = (rec.date_end - today).days if rec.date_end else 0

    @api.depends('date_start', 'date_end')
    def _compute_progress(self):
        today = date.today()
        for rec in self:
            if rec.date_start and rec.date_end:
                total = (rec.date_end - rec.date_start).days
                elapsed = (today - rec.date_start).days
                rec.progress = min(100.0, max(0.0, (elapsed / total) * 100)) if total > 0 else 100.0
            else:
                rec.progress = 0.0

    @api.depends('date_end', 'notice_days', 'state')
    def _compute_is_near_expiry(self):
        today = date.today()
        for rec in self:
            if rec.date_end and rec.state == 'active':
                delta = (rec.date_end - today).days
                rec.is_near_expiry = 0 <= delta <= rec.notice_days
            else:
                rec.is_near_expiry = False

    @api.depends('date_end', 'state')
    def _compute_is_expired(self):
        today = date.today()
        for rec in self:
            if rec.date_end and rec.state not in ('cancelled', 'renewed'):
                rec.is_expired = rec.date_end < today
            else:
                rec.is_expired = False

    @api.depends('is_near_expiry', 'is_expired', 'state')
    def _compute_health_status(self):
        for rec in self:
            if rec.is_expired or rec.state in ('expired', 'cancelled'):
                rec.health_status = 'red'
            elif rec.is_near_expiry:
                rec.health_status = 'orange'
            else:
                rec.health_status = 'green'

    _BILLING_TO_MONTHS = {
        'monthly': 1,
        'quarterly': 3,
        'semi_annual': 6,
        'annual': 12,
    }

    @api.depends('amount_total', 'billing_frequency', 'state')
    def _compute_mrr(self):
        for rec in self:
            months = rec._BILLING_TO_MONTHS.get(rec.billing_frequency)
            if rec.state == 'active' and months and rec.amount_total:
                rec.mrr = rec.amount_total / months
            else:
                rec.mrr = 0.0

    @api.depends('amendment_ids')
    def _compute_amendment_count(self):
        for rec in self:
            rec.amendment_count = len(rec.amendment_ids)

    @api.depends(
        'description', 'amount_total', 'approval_line_ids.state', 'state',
        'create_date', 'date_signed', 'milestone_ids.state', 'partner_id',
    )
    def _compute_risk_score(self):
        """Computes a 0-100 contract risk score from weighted criteria:
        missing termination clause (25), high amount without a recorded
        approval (20), signature delay (20), overdue milestones (20),
        and partner history (15)."""
        for rec in self:
            score = 0
            factors = []

            description_text = (rec.description or '').lower()
            termination_keywords = ['termination', 'terminate', 'notice period']
            if not any(kw in description_text for kw in termination_keywords):
                score += 25
                factors.append(_("No termination clause identified in the content (+25)"))

            if rec.amount_total and rec.amount_total > 50000:
                has_approval = bool(rec.approval_line_ids.filtered(lambda l: l.state == 'approved'))
                if not has_approval and rec.state not in ('draft', 'negotiation'):
                    score += 20
                    factors.append(_("High amount (> 50,000) without a recorded approval step (+20)"))

            if rec.state in ('negotiation', 'pending_approval') and rec.create_date:
                days_open = (fields.Date.today() - rec.create_date.date()).days
                if days_open > 30:
                    score += 20
                    factors.append(_(
                        "In negotiation/approval for more than 30 days without a signature (+20)"
                    ))

            late_milestones = rec.milestone_ids.filtered(lambda m: m.state == 'late')
            if late_milestones:
                score += 20
                factors.append(_("%d overdue milestone(s) (+20)") % len(late_milestones))

            if rec.partner_id:
                partner_contracts = self.search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('id', '!=', rec.id),
                ])
                total_partner = len(partner_contracts)
                if total_partner >= 3:
                    bad_history = len(partner_contracts.filtered(
                        lambda c: c.state in ('cancelled', 'expired')
                    ))
                    if total_partner and (bad_history / total_partner) > 0.3:
                        score += 15
                        factors.append(_(
                            "Partner history: %d%% of contracts cancelled/expired (+15)"
                        ) % round((bad_history / total_partner) * 100))

            rec.risk_score = min(100, score)
            if rec.risk_score >= 60:
                rec.risk_level = 'high'
            elif rec.risk_score >= 30:
                rec.risk_level = 'medium'
            else:
                rec.risk_level = 'low'
            rec.risk_factors = '\n'.join(factors) if factors else _("No risk factors identified.")

    @api.depends('sale_order_ids', 'purchase_order_ids')
    def _compute_order_counts(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)
            rec.purchase_order_count = len(rec.purchase_order_ids)

    @api.depends('child_contract_ids')
    def _compute_renewal_count(self):
        for rec in self:
            rec.renewal_count = len(rec.child_contract_ids)

    def _compute_amount_invoiced(self):
        for rec in self:
            if not rec.id:
                rec.amount_invoiced = 0.0
                rec.amount_remaining = rec.amount_total
                continue
            invoices = self.env['account.move'].search([
                ('contract_id', '=', rec.id),
                ('move_type', 'in', ['out_invoice', 'in_invoice']),
                ('state', '=', 'posted'),
            ])
            contract_currency = rec.currency_id or rec.company_id.currency_id
            invoiced = 0.0
            for move in invoices:
                amount = move.amount_untaxed
                if move.currency_id and move.currency_id != contract_currency:
                    amount = move.currency_id._convert(
                        amount,
                        contract_currency,
                        move.company_id or rec.company_id,
                        move.date or fields.Date.today(),
                    )
                invoiced += amount
            rec.amount_invoiced = invoiced
            rec.amount_remaining = max(0.0, (rec.amount_total or 0.0) - invoiced)

    def _compute_document_count(self):
        for rec in self:
            if not rec.id:
                rec.document_count = 0
                continue
            rec.document_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'contract.contract'),
                ('res_id', '=', rec.id),
            ])

    @api.model
    def _name_search(self, name='', args=None, operator='ilike',
                     limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args = ['|', ('name', operator, name), ('title', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def _compute_access_url(self):
        super()._compute_access_url()
        for contract in self:
            contract.access_url = '/my/contracts/%s' % contract.id

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            content = self.template_id.content or ''
            replacements = {
                '{{partner_name}}': self.partner_id.name or '',
                '{{date_start}}': str(self.date_start) if self.date_start else '',
                '{{date_end}}': str(self.date_end) if self.date_end else '',
                '{{amount_total}}': str(self.amount_total) if self.amount_total else '0',
                '{{company_name}}': self.company_id.name or '',
                '{{user_name}}': self.user_id.name or '',
                '{{contract_ref}}': self.name or '',
            }
            for var, val in replacements.items():
                content = content.replace(var, val)
            self.description = content
            self.contract_type = self.template_id.contract_type
            self.notice_days = self.template_id.notice_days
            self.renewal_type = self.template_id.renewal_type
            self.renewal_duration = self.template_id.renewal_duration
            self.renewal_duration_unit = self.template_id.renewal_duration_unit

    @api.onchange('duration_type')
    def _onchange_duration(self):
        if self.duration_type == 'indefinite':
            self.date_end = False

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_end and rec.date_start and rec.date_end < rec.date_start:
                raise ValidationError(_('The end date must be later than the start date.'))

    @api.constrains('amount_total')
    def _check_amount(self):
        for rec in self:
            if rec.amount_total and rec.amount_total < 0:
                raise ValidationError(_('The contract value cannot be negative.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('contract.contract') or 'New'
                )
        return super().create(vals_list)

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': 'New',
            'state': 'draft',
            'version': 1,
            'date_signed': False,
            'signed_by_us': False,
            'signed_by_partner': False,
            'signature_our': False,
            'signature_partner': False,
            'parent_contract_id': False,
            'title': _('%s (copy)') % self.title,
            'milestone_ids': [(5, 0, 0)],
        })
        return super().copy(default)

    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})
        self.message_post(
            body=_('Reset to draft by <strong>%s</strong>.') % self.env.user.name,
            message_type='comment', subtype_xmlid='mail.mt_note',
        )

    def action_negotiate(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Please select a partner before starting the negotiation.'))
        self.write({'state': 'negotiation'})
        self.message_post(
            body=_('Negotiation started by <strong>%s</strong> with %s.') % (
                self.env.user.name, self.partner_id.name,
            ),
            message_type='comment', subtype_xmlid='mail.mt_note',
        )
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('Negotiation in progress'),
            note=_('Contract %s is under negotiation with %s.') % (
                self.name, self.partner_id.name,
            ),
            user_id=self.user_id.id or self.env.user.id,
        )

    def action_submit_approval(self):
        self.ensure_one()
        ApprovalRule = self.env['contract.approval.rule']
        rule = ApprovalRule._find_rule_for_amount(self.amount_total, self.company_id)

        self.approval_line_ids.unlink()

        if rule and rule.approval_level_ids:
            lines = []
            for level in rule.approval_level_ids:
                lines.append((0, 0, {
                    'sequence': level.sequence,
                    'name': level.name,
                    'group_id': level.group_id.id if level.group_id else False,
                    'user_id': level.user_id.id if level.user_id else False,
                    'state': 'pending',
                }))
            self.write({'state': 'pending_approval', 'approval_line_ids': lines})
            self.message_post(
                body=_(
                    'Submitted for approval by <strong>%s</strong> '
                    '— matrix "%s": %d level(s).'
                ) % (self.env.user.name, rule.name, len(rule.approval_level_ids)),
                message_type='comment', subtype_xmlid='mail.mt_note',
            )
            self._notify_current_approval_level()
        else:
            if not self.approver_id:
                raise UserError(_(
                    "Please assign an approver for this contract, or "
                    "configure an amount-based approval matrix."
                ))
            self.write({'state': 'pending_approval'})
            self.message_post(
                body=_('Submitted for approval by <strong>%s</strong> → %s.') % (
                    self.env.user.name, self.approver_id.name,
                ),
                message_type='comment', subtype_xmlid='mail.mt_note',
            )
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Approval required'),
                note=_('Contract %s requires your approval.') % self.name,
                user_id=self.approver_id.id,
            )
            template = self.env.ref(
                'smart_contract_lifecycle.mail_template_contract_approval',
                raise_if_not_found=False,
            )
            if template:
                template.send_mail(self.id, force_send=False)

    def _notify_current_approval_level(self):
        """Schedules an activity for the user(s) responsible for the
        current approval step."""
        self.ensure_one()
        current = self.current_approval_line_id
        if not current:
            return
        users = current.user_id or current.group_id.users
        for user in users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Approval required — %s') % current.name,
                note=_('Contract %s requires your approval (level "%s").') % (
                    self.name, current.name,
                ),
                user_id=user.id,
            )

    @api.depends('approval_line_ids.state', 'approval_line_ids.sequence')
    def _compute_current_approval_line(self):
        for rec in self:
            pending = rec.approval_line_ids.filtered(lambda l: l.state == 'pending')
            rec.current_approval_line_id = pending[:1]
            total = len(rec.approval_line_ids)
            done = len(rec.approval_line_ids.filtered(lambda l: l.state == 'approved'))
            rec.approval_progress = _('%d / %d levels approved') % (done, total) if total else ''

    @api.depends('current_approval_line_id', 'approver_id', 'state', 'approval_line_ids')
    def _compute_can_user_approve(self):
        user = self.env.user
        is_manager = user.has_group('smart_contract_lifecycle.group_contract_manager')
        for rec in self:
            if rec.state != 'pending_approval':
                rec.can_user_approve = False
            elif is_manager:
                rec.can_user_approve = True
            elif rec.approval_line_ids:
                current = rec.current_approval_line_id
                rec.can_user_approve = bool(current and current.can_approve(user))
            else:
                rec.can_user_approve = bool(rec.approver_id and rec.approver_id == user)

    def action_approve(self):
        self.ensure_one()

        if self.approval_line_ids:
            current = self.current_approval_line_id
            if not current:
                raise UserError(_("All approval steps have already been processed."))
            if not current.can_approve(self.env.user) and not self.env.user.has_group(
                'smart_contract_lifecycle.group_contract_manager'
            ):
                raise UserError(_(
                    "You are not authorized to approve the step \"%s\"."
                ) % current.name)

            current.write({
                'state': 'approved',
                'approved_by_id': self.env.user.id,
                'date_done': fields.Datetime.now(),
            })
            self.message_post(
                body=_('Step "%s" approved by <strong>%s</strong>.') % (
                    current.name, self.env.user.name,
                ),
                message_type='comment', subtype_xmlid='mail.mt_note',
            )

            remaining = self.approval_line_ids.filtered(lambda l: l.state == 'pending')
            if remaining:
                self._notify_current_approval_level()
                return

            self.write({'state': 'active', 'date_signed': fields.Date.today()})
            self.message_post(
                body=_('All approval steps have been validated. Contract activated on %s.') % (
                    fields.Date.today(),
                ),
                message_type='comment', subtype_xmlid='mail.mt_note',
            )
            return

        if (
            self.approver_id
            and self.approver_id != self.env.user
            and not self.env.user.has_group('smart_contract_lifecycle.group_contract_manager')
        ):
            raise UserError(_("Only the designated approver or a manager can approve this contract."))
        self.write({'state': 'active', 'date_signed': fields.Date.today()})
        self.message_post(
            body=_('Contract approved and activated by <strong>%s</strong> on %s.') % (
                self.env.user.name, fields.Date.today(),
            ),
            message_type='comment', subtype_xmlid='mail.mt_note',
        )

    def action_activate(self):
        self.ensure_one()
        self.write({'state': 'active', 'date_signed': self.date_signed or fields.Date.today()})
        self.message_post(
            body=_('Contract activated directly by <strong>%s</strong> on %s.') % (
                self.env.user.name, fields.Date.today(),
            ),
            message_type='comment', subtype_xmlid='mail.mt_note',
        )

    def action_suspend(self):
        self.ensure_one()
        if self.state != 'active':
            raise UserError(_('Only an active contract can be suspended.'))
        self.write({'state': 'suspended'})
        self.message_post(
            body=_('Contract suspended by <strong>%s</strong> on %s.') % (
                self.env.user.name, fields.Date.today(),
            ),
            message_type='comment', subtype_xmlid='mail.mt_note',
        )

    def action_reactivate(self):
        self.ensure_one()
        if self.state != 'suspended':
            raise UserError(_('Only a suspended contract can be reactivated.'))
        self.write({'state': 'active'})
        self.message_post(
            body=_('Contract reactivated by <strong>%s</strong> on %s.') % (
                self.env.user.name, fields.Date.today(),
            ),
            message_type='comment', subtype_xmlid='mail.mt_note',
        )

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'renewed':
                raise UserError(_('A renewed contract cannot be cancelled directly.'))
        self.write({'state': 'cancelled'})
        for rec in self:
            rec.message_post(
                body=_('Contract cancelled by <strong>%s</strong> on %s.') % (
                    self.env.user.name, fields.Date.today(),
                ),
                message_type='comment', subtype_xmlid='mail.mt_note',
            )

    def action_renew(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Renew Contract'),
            'res_model': 'contract.renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contract_id': self.id},
        }

    def action_view_amendments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Amendments'),
            'res_model': 'contract.amendment',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_view_renewals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Renewals'),
            'res_model': 'contract.contract',
            'view_mode': 'list,form',
            'domain': [('parent_contract_id', '=', self.id)],
        }

    def action_view_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Documents — %s') % self.name,
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [
                ('res_model', '=', 'contract.contract'),
                ('res_id', '=', self.id),
            ],
            'context': {
                'default_res_model': 'contract.contract',
                'default_res_id': self.id,
            },
        }

    def action_view_sale_orders(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Quotations / Orders — %s') % self.name,
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }
        if len(self.sale_order_ids) == 1:
            action.update({'view_mode': 'form', 'res_id': self.sale_order_ids.id})
        return action

    def action_create_sale_order(self):
        """Creates an empty pre-filled quotation and links it to this contract."""
        self.ensure_one()
        if self.contract_type not in ('customer', 'service', 'partnership'):
            raise UserError(_(
                "Creating a quotation is only relevant for a customer, "
                "service, or partnership contract."
            ))
        order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
        })
        self.write({'sale_order_ids': [(4, order.id)]})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quotation'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': order.id,
        }

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Orders — %s') % self.name,
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }
        if len(self.purchase_order_ids) == 1:
            action.update({'view_mode': 'form', 'res_id': self.purchase_order_ids.id})
        return action

    def action_create_purchase_order(self):
        """Creates an empty pre-filled vendor order and links it to this contract."""
        self.ensure_one()
        if self.contract_type not in ('supplier', 'partnership'):
            raise UserError(_(
                "Creating a vendor order is only relevant for a vendor "
                "or partnership contract."
            ))
        order = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
        })
        self.write({'purchase_order_ids': [(4, order.id)]})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Order'),
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': order.id,
        }

    def action_create_amendment(self):
        self.ensure_one()
        if self.state != 'active':
            raise UserError(_("An amendment can only be created on an active contract."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Amendment'),
            'res_model': 'contract.amendment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }

    def action_send_contract(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send Contract'),
            'res_model': 'contract.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contract_id': self.id},
        }

    def action_insert_clauses(self):
        self.ensure_one()
        if self.state not in ('draft', 'negotiation'):
            raise UserError(_(
                "Clauses can only be inserted on a contract in draft "
                "or negotiation state."
            ))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Insert Clauses'),
            'res_model': 'contract.clause.insert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contract_id': self.id},
        }

    def action_print_contract(self):
        return self.env.ref('smart_contract_lifecycle.action_report_contract').report_action(self)

    @api.model
    def _cron_check_expiry(self):
        self = self.sudo()
        today = date.today()

        contracts_to_renew = self.search([
            ('state', '=', 'active'),
            ('renewal_type', '=', 'automatic'),
            ('date_end', '=', today),
        ])
        for contract in contracts_to_renew:
            try:
                contract._do_auto_renew()
                _logger.info('Auto-renewal: %s', contract.name)
            except Exception as e:
                _logger.error('Auto-renewal failed for %s: %s', contract.name, e)

        contracts_to_expire = self.search([
            ('state', '=', 'active'),
            ('date_end', '<', today),
        ])
        if contracts_to_expire:
            contracts_to_expire.write({'state': 'expired'})
            _logger.info('Contracts automatically expired: %s', contracts_to_expire.mapped('name'))

        alert_contracts = self.search([
            ('state', '=', 'active'),
            ('date_end', '!=', False),
            ('is_near_expiry', '=', True),
        ])
        for contract in alert_contracts:
            existing = self.env['mail.activity'].search([
                ('res_id', '=', contract.id),
                ('res_model', '=', 'contract.contract'),
                ('summary', '=', _('Contract expiry alert')),
                ('active', '=', True),
            ], limit=1)
            if not existing:
                contract.activity_schedule(
                    'mail.mail_activity_data_warning',
                    summary=_('Contract expiry alert'),
                    note=_('Contract %s expires on %s (%s days remaining).') % (
                        contract.name, contract.date_end, contract.days_remaining,
                    ),
                    user_id=contract.user_id.id or self.env.ref('base.user_root').id,
                )
                template = self.env.ref(
                    'smart_contract_lifecycle.mail_template_contract_expiry_alert',
                    raise_if_not_found=False,
                )
                if template:
                    template.send_mail(contract.id, force_send=False)

    def _do_auto_renew(self):
        self.ensure_one()
        unit = self.renewal_duration_unit or 'months'
        duration = self.renewal_duration or 12
        delta_map = {
            'days': relativedelta(days=duration),
            'months': relativedelta(months=duration),
            'years': relativedelta(years=duration),
        }
        delta = delta_map.get(unit, relativedelta(months=12))
        new_start = self.date_end + relativedelta(days=1)
        new_end = new_start + delta - relativedelta(days=1)
        new_contract = self.copy({
            'title': _('%s (Renewal)') % self.title,
            'date_start': new_start,
            'date_end': new_end,
            'parent_contract_id': self.id,
            'state': 'active',
            'milestone_ids': [(5, 0, 0)],
        })
        new_contract.write({'version': self.version + 1})
        self.write({'state': 'renewed'})
        self.message_post(
            body=_('Contract automatically renewed → <a href="/odoo/contracts/%s">%s</a>') % (
                new_contract.id, new_contract.name,
            ),
            message_type='comment', subtype_xmlid='mail.mt_note',
        )
        return new_contract


class ContractTag(models.Model):
    _name = 'contract.tag'
    _description = 'Contract Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')
    contract_count = fields.Integer(string='Contracts', compute='_compute_contract_count')

    def _compute_contract_count(self):
        for tag in self:
            tag.contract_count = self.env['contract.contract'].search_count(
                [('tag_ids', 'in', tag.id)]
            )
