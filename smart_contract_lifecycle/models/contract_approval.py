from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ContractApprovalRule(models.Model):
    _name = 'contract.approval.rule'
    _description = "Approval Matrix Rule"
    _order = 'sequence, amount_min'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company, required=True,
    )
    amount_min = fields.Monetary(string='Minimum Amount', default=0.0)
    amount_max = fields.Monetary(
        string='Maximum Amount', default=0.0,
        help="0 = no upper limit (highest bracket).",
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    approval_level_ids = fields.One2many(
        'contract.approval.rule.level', 'rule_id', string="Approval Levels",
    )
    active = fields.Boolean(default=True)

    @api.constrains('amount_min', 'amount_max')
    def _check_amounts(self):
        for rec in self:
            if rec.amount_max and rec.amount_max <= rec.amount_min:
                raise UserError(_(
                    "The maximum amount must be greater than the minimum "
                    "amount (rule \"%s\")."
                ) % rec.name)

    @api.model
    def _find_rule_for_amount(self, amount, company):
        """Returns the first rule matching the given amount."""
        domain = [
            ('company_id', '=', company.id),
            ('amount_min', '<=', amount),
            '|', ('amount_max', '=', 0.0), ('amount_max', '>', amount),
        ]
        return self.search(domain, order='amount_min desc', limit=1)


class ContractApprovalRuleLevel(models.Model):
    _name = 'contract.approval.rule.level'
    _description = "Approval Matrix Level"
    _order = 'sequence'

    rule_id = fields.Many2one(
        'contract.approval.rule', string='Rule', required=True, ondelete='cascade',
    )
    sequence = fields.Integer(string='Order', default=10)
    name = fields.Char(string='Level Name', required=True)
    group_id = fields.Many2one(
        'res.groups', string='Approver Group',
        help="Any member of this group can approve this level.",
    )
    user_id = fields.Many2one(
        'res.users', string='Specific Approver',
        help="If set, only this user can approve this level "
             "(takes precedence over the group).",
    )

    @api.constrains('group_id', 'user_id')
    def _check_approver_defined(self):
        for rec in self:
            if not rec.group_id and not rec.user_id:
                raise UserError(_(
                    "Level \"%s\" must define an approver group or a "
                    "specific user."
                ) % rec.name)


class ContractApprovalLine(models.Model):
    """Instance of an approval level for a given contract, created when
    the contract is submitted for approval."""
    _name = 'contract.approval.line'
    _description = "Contract Approval Step"
    _order = 'sequence'

    contract_id = fields.Many2one(
        'contract.contract', string='Contract', required=True, ondelete='cascade',
    )
    sequence = fields.Integer(string='Order')
    name = fields.Char(string='Level Name', required=True)
    group_id = fields.Many2one('res.groups', string='Approver Group')
    user_id = fields.Many2one('res.users', string='Specific Approver')
    approved_by_id = fields.Many2one(
        'res.users', string='Approved By', readonly=True,
    )
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending')
    date_done = fields.Datetime(string='Processing Date', readonly=True)

    def can_approve(self, user=None):
        user = user or self.env.user
        self.ensure_one()
        if self.user_id:
            return self.user_id == user
        if self.group_id:
            return self.group_id in user.groups_id
        return False
