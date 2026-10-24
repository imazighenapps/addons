# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ExpensePolicy(models.Model):
    _name = "expense.policy"
    _description = "Expense Policy"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    categ_id = fields.Many2one(
        "product.category", string="Expense Category",
        help="Leave empty to apply to every expense category.")
    product_id = fields.Many2one(
        "product.product", string="Expense Product",
        help="Leave empty to apply to every product.")
    max_amount = fields.Monetary(
        currency_field="currency_id",
        help="Maximum reimbursable amount. Zero means no cap.")
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    require_receipt = fields.Boolean(default=True)
    max_age_days = fields.Integer(
        default=90, help="Maximum number of days between the expense date "
                         "and the submission. Zero disables the check.")
    block_mode = fields.Selection(
        [("block", "Block submission"), ("warn", "Warn the approver")],
        default="block", required=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    def _matches(self, expense):
        self.ensure_one()
        if expense.company_id != self.company_id:
            return False
        if self.product_id and expense.product_id != self.product_id:
            return False
        if self.categ_id and expense.product_id.categ_id != self.categ_id:
            return False
        return True

    def _violations(self, expense):
        self.ensure_one()
        problems = []
        if self.max_amount and expense.total_amount_currency > self.max_amount:
            problems.append(_(
                "Amount %(amount).2f exceeds the cap of %(cap).2f.",
                amount=expense.total_amount_currency, cap=self.max_amount))
        if self.require_receipt and not expense.attachment_ids:
            problems.append(_("A receipt is required."))
        if self.max_age_days and expense.date:
            age = (fields.Date.context_today(self) - expense.date).days
            if age > self.max_age_days:
                problems.append(_(
                    "The expense is %(age)s days old, the maximum is %(max)s.",
                    age=age, max=self.max_age_days))
        return problems


class ExpenseAudit(models.Model):
    _name = "expense.audit"
    _description = "Expense Policy Violation"
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True)
    expense_id = fields.Many2one(
        "hr.expense", string="Expense", required=True,
        ondelete="cascade", index=True)
    policy_id = fields.Many2one(
        "expense.policy", string="Policy", ondelete="set null")
    level = fields.Selection(
        [("warning", "Warning"), ("block", "Blocked")], required=True)
    message = fields.Char(required=True)
    employee_id = fields.Many2one(
        related="expense_id.employee_id", store=True, string="Employee")
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "expense.audit") or "/"
        return super().create(vals_list)


class HrExpense(models.Model):
    _inherit = "hr.expense"

    policy_state = fields.Selection(
        [("ok", "Compliant"), ("warned", "Warning"),
         ("blocked", "Blocked")],
        string="Policy", default="ok", readonly=True, copy=False,
        tracking=True)
    policy_note = fields.Text(string="Policy Messages", readonly=True,
                              copy=False)

    def _run_expense_policy(self):
        """Return (blocking_messages, warning_messages) and log violations."""
        blocking, warnings = [], []
        policies = self.env["expense.policy"].search([
            ("active", "=", True),
            ("company_id", "=", self.company_id.id),
        ])
        for expense in self:
            expense_blocking, expense_warning = [], []
            for policy in policies.filtered(lambda p: p._matches(expense)):
                problems = policy._violations(expense)
                for problem in problems:
                    if policy.block_mode == "block":
                        expense_blocking.append("%s: %s" % (policy.name, problem))
                    else:
                        expense_warning.append("%s: %s" % (policy.name, problem))
                    self.env["expense.audit"].create({
                        "expense_id": expense.id,
                        "policy_id": policy.id,
                        "level": "block" if policy.block_mode == "block"
                                 else "warning",
                        "message": problem,
                        "company_id": expense.company_id.id,
                    })
            if expense_blocking:
                expense.policy_state = "blocked"
            elif expense_warning:
                expense.policy_state = "warned"
            else:
                expense.policy_state = "ok"
            messages = expense_blocking + expense_warning
            expense.policy_note = "\n".join(messages) if messages else False
            if expense_blocking:
                blocking += ["[%s] %s" % (expense.name or expense.id, m)
                             for m in expense_blocking]
            if expense_warning:
                warnings += ["[%s] %s" % (expense.name or expense.id, m)
                             for m in expense_warning]
        return blocking, warnings

    def action_submit(self):
        blocking, warnings = self._run_expense_policy()
        if blocking:
            raise UserError(_(
                "This expense does not comply with your policy:\n%s",
                "\n".join(blocking)))
        for expense in self:
            if any(line for line in (expense.policy_note or "").splitlines()):
                expense.message_post(body=_(
                    "Expense policy warning:\n%s", expense.policy_note))
        # Odoo 18 submits an expense through ``action_submit_expenses``.
        parent = super()
        if hasattr(parent, "action_submit"):
            return parent.action_submit()
        if hasattr(parent, "action_submit_expenses"):
            return parent.action_submit_expenses()
        return True
