# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DeferralSchedule(models.Model):
    _name = "deferral.schedule"
    _description = "Deferred Expense and Revenue Schedule"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    code = fields.Char(
        required=True, copy=False, tracking=True,
        help="Reference of the schedule, generated from the DFR sequence "
             "when it is left empty.")
    schedule_type = fields.Selection(
        [("expense", "Prepaid Expense"), ("revenue", "Deferred Revenue")],
        default="expense", required=True, tracking=True,
        help="A prepaid expense spreads a cost already paid over several "
             "months, a deferred revenue spreads an income already invoiced.")
    partner_id = fields.Many2one(
        "res.partner", string="Partner", tracking=True,
        help="Supplier of the prepaid expense or customer of the deferred "
             "revenue.")
    invoice_ref = fields.Char(
        string="Invoice Reference",
        help="Supplier bill or customer invoice this schedule comes from.")
    journal_id = fields.Many2one(
        "account.journal", string="Journal",
        domain="[('type', '=', 'general')]",
        help="General journal used for the monthly entries. Leave it empty "
             "to post the lines without creating a journal entry.")
    account_id = fields.Many2one(
        "account.account", string="Deferral Account", tracking=True,
        help="Account that receives the monthly expense or revenue.")
    offset_account_id = fields.Many2one(
        "account.account", string="Offset Account", tracking=True,
        help="Counterpart account used on the monthly journal entry.")
    amount = fields.Monetary(
        required=True, currency_field="currency_id", tracking=True,
        help="Total amount to spread over the whole period.")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    date_start = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(
        required=True, tracking=True,
        default=lambda self: fields.Date.context_today(self)
        + relativedelta(months=12, days=-1))
    period_count = fields.Integer(
        string="Periods", compute="_compute_periods", store=True,
        help="Number of monthly periods covered by the schedule.")
    monthly_amount = fields.Monetary(
        string="Monthly Amount", currency_field="currency_id",
        compute="_compute_periods", store=True)
    posted_amount = fields.Monetary(
        string="Posted Amount", currency_field="currency_id",
        readonly=True, copy=False, tracking=True)
    remaining_amount = fields.Monetary(
        string="Remaining Amount", currency_field="currency_id",
        compute="_compute_remaining", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("done", "Done"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "deferral.line", "schedule_id", string="Schedule Lines", copy=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_company_uniq', "UNIQUE(code, company_id)", "The schedule code must be unique per company."),
    ]

    @api.depends("date_start", "date_end", "amount")
    def _compute_periods(self):
        for schedule in self:
            count = schedule._month_count()
            schedule.period_count = count
            schedule.monthly_amount = schedule.amount / count if count else 0.0

    @api.depends("amount", "posted_amount")
    def _compute_remaining(self):
        for schedule in self:
            schedule.remaining_amount = (
                schedule.amount - schedule.posted_amount)

    def _month_count(self):
        """Number of monthly periods between the two dates, days included."""
        self.ensure_one()
        if not self.date_start or not self.date_end \
                or self.date_end < self.date_start:
            return 0
        months = ((self.date_end.year - self.date_start.year) * 12
                  + self.date_end.month - self.date_start.month)
        if self.date_end.day >= self.date_start.day:
            months += 1
        return max(months, 1)

    @api.model_create_multi
    def create(self, vals_list):
        seen = set()
        for vals in vals_list:
            code = (vals.get("code") or "").strip()
            if not code:
                code = self.env["ir.sequence"].next_by_code(
                    "deferral.schedule") or "/"
            vals["code"] = code
            if vals.get("name", "/") == "/":
                vals["name"] = code
            company_id = vals.get("company_id") or self.env.company.id
            key = (code, company_id)
            if key in seen:
                raise ValidationError(_(
                    "The schedule code \"%s\" is used twice in the same "
                    "company.", code))
            seen.add(key)
            duplicate = self.with_context(active_test=False).search([
                ("code", "=", code),
                ("company_id", "=", company_id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "The schedule code \"%s\" is already used by the "
                    "schedule \"%s\" of the same company.",
                    code, duplicate.name))
        return super().create(vals_list)

    def write(self, vals):
        if any(field in vals
               for field in ("amount", "date_start", "date_end")):
            for schedule in self:
                if schedule.state != "draft":
                    raise UserError(_(
                        "The amount and the period of the schedule \"%s\" "
                        "can only be changed while it is in draft.",
                        schedule.name))
        return super().write(vals)

    @api.constrains("date_start", "date_end")
    def _check_period(self):
        for schedule in self:
            if schedule.date_end < schedule.date_start:
                raise ValidationError(_(
                    "The end date cannot be before the start date."))
            if schedule._month_count() < 1:
                raise ValidationError(_(
                    "A schedule must cover at least one monthly period."))

    @api.constrains("amount")
    def _check_amount(self):
        for schedule in self:
            if schedule.amount <= 0:
                raise ValidationError(_(
                    "The deferred amount of \"%s\" must be greater than "
                    "zero.", schedule.name))

    def _sync_posted(self):
        """Recompute the posted amount and close the schedule when complete."""
        for schedule in self:
            posted = sum(schedule.line_ids.filtered(
                lambda line: line.state == "posted").mapped("amount"))
            schedule.posted_amount = schedule.currency_id.round(posted)
            if schedule.state == "running" and schedule.line_ids \
                    and not schedule.line_ids.filtered(
                        lambda line: line.state == "draft"):
                schedule.state = "done"
                schedule.message_post(body=_(
                    "All %(count)s periods are posted: the schedule is "
                    "complete.", count=len(schedule.line_ids)))

    def _create_move(self, line):
        """Build and post the journal entry of one period, if configured."""
        self.ensure_one()
        if not (self.journal_id and self.account_id
                and self.offset_account_id):
            return False
        if self.schedule_type == "revenue":
            debit_account = self.offset_account_id
            credit_account = self.account_id
        else:
            debit_account = self.account_id
            credit_account = self.offset_account_id
        label = "%(code)s - %(date)s" % {
            "code": self.code, "date": line.date}
        move = self.env["account.move"].create({
            "move_type": "entry",
            "journal_id": self.journal_id.id,
            "date": line.date,
            "ref": label,
            "line_ids": [
                (0, 0, {
                    "name": label,
                    "account_id": debit_account.id,
                    "debit": line.amount,
                    "credit": 0.0,
                    "partner_id": self.partner_id.id,
                }),
                (0, 0, {
                    "name": label,
                    "account_id": credit_account.id,
                    "debit": 0.0,
                    "credit": line.amount,
                    "partner_id": self.partner_id.id,
                }),
            ],
        })
        move.action_post()
        return move

    def action_start(self):
        for schedule in self:
            if schedule.state != "draft":
                raise UserError(_(
                    "Only a draft schedule can be started."))
            if schedule.amount <= 0:
                raise UserError(_(
                    "Set a deferred amount before starting the schedule "
                    "\"%s\".", schedule.name))
            if schedule.line_ids:
                raise UserError(_(
                    "The schedule \"%s\" already has lines. Remove them "
                    "before starting it again.", schedule.name))
            count = schedule.period_count
            if count < 1:
                raise UserError(_(
                    "The schedule \"%s\" must cover at least one monthly "
                    "period.", schedule.name))
            base = schedule.currency_id.round(schedule.amount / count)
            left = schedule.amount
            commands = []
            for index in range(count):
                line_date = schedule.date_start + relativedelta(months=index)
                if line_date > schedule.date_end:
                    line_date = schedule.date_end
                line_amount = base if index < count - 1 else \
                    schedule.currency_id.round(left)
                left -= line_amount
                commands.append((0, 0, {
                    "sequence": (index + 1) * 10,
                    "date": line_date,
                    "amount": line_amount,
                }))
            schedule.write({"line_ids": commands, "state": "running"})
            schedule.message_post(body=_(
                "Schedule started: %(count)s monthly line(s) of about "
                "%(monthly)s each.", count=count,
                monthly=schedule.monthly_amount))
        return True

    def action_post_next(self):
        for schedule in self:
            if schedule.state != "running":
                raise UserError(_(
                    "Only a running schedule can post lines. Start the "
                    "schedule \"%s\" first.", schedule.name))
            line = schedule.line_ids.filtered(
                lambda item: item.state == "draft").sorted(
                    lambda item: (item.sequence, item.date, item.id))[:1]
            if not line:
                raise UserError(_(
                    "Every line of the schedule \"%s\" is already posted.",
                    schedule.name))
            line.action_post()
        return True

    def action_post_all(self):
        for schedule in self:
            if schedule.state != "running":
                raise UserError(_(
                    "Only a running schedule can post lines. Start the "
                    "schedule \"%s\" first.", schedule.name))
            draft_lines = schedule.line_ids.filtered(
                lambda item: item.state == "draft").sorted(
                    lambda item: (item.sequence, item.date, item.id))
            if not draft_lines:
                raise UserError(_(
                    "There is no draft line left to post on the schedule "
                    "\"%s\".", schedule.name))
            for line in draft_lines:
                line.action_post()
        return True

    def action_done(self):
        for schedule in self:
            if schedule.state != "running":
                raise UserError(_(
                    "Only a running schedule can be closed."))
            if schedule.line_ids.filtered(
                    lambda line: line.state == "draft"):
                raise UserError(_(
                    "Post or remove the remaining draft lines before "
                    "closing the schedule \"%s\".", schedule.name))
            schedule.state = "done"
            schedule.message_post(body=_(
                "Schedule closed with %(posted)s posted out of "
                "%(amount)s.", posted=schedule.posted_amount,
                amount=schedule.amount))
        return True

    def action_cancel(self):
        for schedule in self:
            if schedule.state not in ("draft", "running"):
                raise UserError(_(
                    "Only a draft or a running schedule can be cancelled."))
            schedule.state = "cancelled"
            schedule.message_post(body=_("Schedule cancelled."))
        return True

    def action_reset(self):
        for schedule in self:
            if schedule.state not in ("cancelled", "done"):
                raise UserError(_(
                    "Only a cancelled or a completed schedule can be reset "
                    "to draft."))
            if schedule.line_ids.filtered(
                    lambda line: line.state == "posted"):
                raise UserError(_(
                    "The schedule \"%s\" already has posted lines: it can "
                    "no longer be reset to draft.", schedule.name))
            schedule.line_ids.unlink()
            schedule.write({"state": "draft", "posted_amount": 0.0})
            schedule.message_post(body=_("Schedule reset to draft."))
        return True


class DeferralLine(models.Model):
    _name = "deferral.line"
    _description = "Deferral Schedule Line"
    _order = "schedule_id, sequence, date, id"

    schedule_id = fields.Many2one(
        "deferral.schedule", string="Schedule", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    date = fields.Date(required=True, default=fields.Date.context_today)
    amount = fields.Monetary(
        required=True, currency_field="currency_id",
        help="Amount expensed or recognised on this period.")
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted")],
        default="draft", required=True, copy=False, index=True)
    move_id = fields.Many2one(
        "account.move", string="Journal Entry", readonly=True, copy=False,
        ondelete="set null")
    currency_id = fields.Many2one(
        related="schedule_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="schedule_id.company_id", store=True, readonly=True)

    def write(self, vals):
        if any(field in vals for field in ("amount", "date")):
            for line in self:
                if line.state == "posted":
                    raise UserError(_(
                        "The posted line of %(date)s can no longer be "
                        "changed.", date=line.date))
        return super().write(vals)

    def unlink(self):
        for line in self:
            if line.state == "posted":
                raise UserError(_(
                    "The posted line of %(date)s cannot be deleted.",
                    date=line.date))
        return super().unlink()

    def action_post(self):
        for line in self:
            schedule = line.schedule_id
            if line.state == "posted":
                raise UserError(_(
                    "The line of %(date)s is already posted.",
                    date=line.date))
            if schedule.state == "cancelled":
                raise UserError(_(
                    "The schedule \"%s\" is cancelled: its lines can no "
                    "longer be posted.", schedule.name))
            if schedule.state == "draft":
                raise UserError(_(
                    "Start the schedule \"%s\" before posting its lines.",
                    schedule.name))
            move = schedule._create_move(line)
            if move:
                line.write({"move_id": move.id})
            line.state = "posted"
            schedule._sync_posted()
        return True
