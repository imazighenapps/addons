# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class ConsolRun(models.Model):
    _name = "consol.run"
    _description = "Consolidation Run"
    _inherit = ["mail.thread"]
    _order = "date_from desc, id desc"

    name = fields.Char(
        required=True, copy=False, default="/", tracking=True,
        help="Reference of the consolidation run. Generated from the CON/ "
             "sequence when left empty.")
    date_from = fields.Date(
        string="From Date", required=True, tracking=True,
        default=lambda self: fields.Date.context_today(self).replace(
            month=1, day=1))
    date_to = fields.Date(
        string="To Date", required=True, tracking=True,
        default=fields.Date.context_today)
    company_ids = fields.Many2many(
        "res.company", string="Companies", required=True, tracking=True,
        default=lambda self: [(6, 0, self.env.company.ids)],
        help="Companies whose posted entries are consolidated. Leave with "
             "the current company alone to consolidate one single ledger.")
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("posted", "Posted")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "consol.line", "run_id", string="Consolidation Lines", copy=False)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    total_debit = fields.Monetary(
        string="Total Debit", currency_field="currency_id",
        compute="_compute_totals", store=True)
    total_credit = fields.Monetary(
        string="Total Credit", currency_field="currency_id",
        compute="_compute_totals", store=True)
    note = fields.Text()

    @api.depends("line_ids.debit", "line_ids.credit")
    def _compute_totals(self):
        for run in self:
            run.total_debit = sum(run.line_ids.mapped("debit"))
            run.total_credit = sum(run.line_ids.mapped("credit"))

    @api.model_create_multi
    def create(self, vals_list):
        seen = set()
        for vals in vals_list:
            name = (vals.get("name") or "").strip()
            if not name or name == "/":
                name = self.env["ir.sequence"].next_by_code(
                    "consol.run") or "/"
            vals["name"] = name
            if name in seen:
                raise ValidationError(_(
                    "The consolidation run name \"%s\" is used twice in the "
                    "same batch.", name))
            seen.add(name)
            duplicate = self.with_context(active_test=False).search([
                ("name", "=", name),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "The consolidation run name \"%s\" is already used by "
                    "another run.", name))
        return super().create(vals_list)

    def write(self, vals):
        locked = {"date_from", "date_to", "company_ids"}
        if locked & set(vals):
            for run in self:
                if run.state == "posted":
                    raise UserError(_(
                        "The period and the companies of the posted "
                        "consolidation run \"%s\" can no longer be changed. "
                        "Reset it to draft first.", run.name))
        return super().write(vals)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for run in self:
            if run.date_to and run.date_from \
                    and run.date_to < run.date_from:
                raise ValidationError(_(
                    "The end date of the consolidation run \"%s\" cannot be "
                    "before its start date.", run.name))

    def action_compute(self):
        for run in self:
            if run.state == "posted":
                raise UserError(_(
                    "The posted consolidation run \"%s\" is locked; reset it "
                    "to draft first.", run.name))
            companies = run.company_ids or self.env.company
            previous = {}
            for line in run.line_ids:
                previous[(line.company_id.id, line.account_code or "")] = (
                    line.mapping or "", line.eliminated)
            data = self.env["account.move.line"].sudo()._read_group(
                [
                    ("parent_state", "=", "posted"),
                    ("date", ">=", run.date_from),
                    ("date", "<=", run.date_to),
                    ("company_id", "in", companies.ids),
                ],
                groupby=["company_id", "account_id"],
                aggregates=["debit:sum", "credit:sum"],
            )
            groups = {}
            for company, account, debit, credit in data:
                if not company or not account:
                    continue
                # Account codes are company-dependent in Odoo 20:
                # read the code for the company of each balance.
                code = account.with_company(company).code or ""
                mapping, eliminated = previous.get(
                    (company.id, code), ("", False))
                if eliminated:
                    debit = credit = 0.0
                else:
                    currency = (
                        company.currency_id or self.env.company.currency_id)
                    if float_is_zero(
                            debit - credit,
                            precision_rounding=currency.rounding):
                        continue
                key = (company.id, code, mapping)
                entry = groups.setdefault(key, {
                    "company": company, "code": code,
                    "name": account.name or "", "mapping": mapping,
                    "debit": 0.0, "credit": 0.0, "eliminated": eliminated,
                })
                entry["debit"] += debit
                entry["credit"] += credit
            dd = [
                {
                    "run_id": run.id,
                    "company_id": entry["company"].id,
                    "account_code": entry["code"],
                    "account_name": entry["name"],
                    "mapping": entry["mapping"],
                    "debit": entry["debit"],
                    "credit": entry["credit"],
                    "eliminated": entry["eliminated"],
                }
                for _, entry in sorted(
                    groups.items(),
                    key=lambda item: (item[0][0], item[0][1], item[0][2]))
            ]
            run.line_ids.unlink()
            if dd:
                self.env["consol.line"].create(dd)
            run.state = "computed"
            run.message_post(body=_(
                "Consolidation computed for %(companies)s between "
                "%(date_from)s and %(date_to)s: %(count)s line(s), "
                "%(debit).2f debit and %(credit).2f credit.",
                companies=", ".join(companies.mapped("name")),
                date_from=run.date_from, date_to=run.date_to,
                count=len(run.line_ids), debit=run.total_debit,
                credit=run.total_credit))
        return True

    def action_eliminate(self):
        for run in self:
            if run.state != "computed":
                raise UserError(_(
                    "The consolidation run \"%s\" must be computed before "
                    "its lines can be eliminated.", run.name))
            lines = run.line_ids.filtered(
                lambda line: line.mapping and not line.eliminated)
            if not lines:
                raise UserError(_(
                    "Tag the intercompany lines of the run \"%s\" with a "
                    "mapping before running the elimination.", run.name))
            lines.write({"eliminated": True, "debit": 0.0, "credit": 0.0})
            run.message_post(body=_(
                "%(count)s line(s) eliminated and zeroed out of the "
                "consolidation.", count=len(lines)))
        return True

    def action_post(self):
        for run in self:
            if run.state != "computed":
                raise UserError(_(
                    "Only a computed consolidation run can be posted."))
            run.state = "posted"
            run.message_post(body=_(
                "Consolidation run posted: the compute and the elimination "
                "are now locked."))
        return True

    def action_reset(self):
        for run in self:
            if run.state not in ("computed", "posted"):
                raise UserError(_(
                    "Only a computed or a posted consolidation run can be "
                    "reset to draft."))
            # Set draft first: the line unlink is forbidden while the run
            # is still posted.
            run.state = "draft"
            run.line_ids.unlink()
            run.message_post(body=_(
                "Consolidation run reset to draft; its lines were cleared."))
        return True

class ConsolLine(models.Model):
    _name = "consol.line"
    _description = "Consolidation Line"
    _order = "run_id, company_id, account_code, id"

    run_id = fields.Many2one(
        "consol.run", string="Consolidation Run", required=True,
        ondelete="cascade", index=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, index=True,
        default=lambda self: self.env.company,
        help="Company whose ledger produced this balance.")
    account_code = fields.Char(string="Account Code", required=True)
    account_name = fields.Char(string="Account Name")
    mapping = fields.Char(
        default="",
        help="Consolidation mapping of the account. Type the same reference "
             "on two reciprocal intercompany lines so the elimination can "
             "zero them together. Preserved when the run is recomputed.")
    debit = fields.Monetary(string="Debit", currency_field="currency_id")
    credit = fields.Monetary(string="Credit", currency_field="currency_id")
    balance = fields.Monetary(
        string="Balance", currency_field="currency_id",
        compute="_compute_balance", store=True,
        help="Debit minus credit.")
    eliminated = fields.Boolean(
        string="Eliminated",
        help="Set when the line was eliminated from the consolidation: its "
             "debit and credit are zeroed.")
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)

    _run_line_uniq = models.Constraint(
        "UNIQUE(run_id, company_id, account_code, mapping)",
        "One consolidation line per company, account code and mapping in a run.")

    @api.depends("debit", "credit")
    def _compute_balance(self):
        for line in self:
            line.balance = line.debit - line.credit

    @api.constrains("debit", "credit")
    def _check_amounts(self):
        for line in self:
            if line.debit < 0 or line.credit < 0:
                raise ValidationError(_(
                    "The debit and the credit of a consolidation line "
                    "cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        run_ids = {vals["run_id"] for vals in vals_list
                   if vals.get("run_id")}
        if run_ids:
            posted = self.env["consol.run"].browse(
                sorted(run_ids)).filtered(
                    lambda run: run.state == "posted")
            if posted:
                raise UserError(_(
                    "The consolidation run \"%s\" is posted: no line can be "
                    "added to it.", posted[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.run_id.state == "posted":
                raise UserError(_(
                    "The consolidation run \"%s\" is posted: its lines can "
                    "no longer be changed.", line.run_id.name))
        return super().write(vals)

    def unlink(self):
        for line in self:
            if line.run_id.state == "posted":
                raise UserError(_(
                    "The consolidation run \"%s\" is posted: its lines can "
                    "no longer be deleted.", line.run_id.name))
        return super().unlink()

    def action_eliminate(self):
        for line in self:
            if line.run_id.state != "computed":
                raise UserError(_(
                    "Only the lines of a computed consolidation run can be "
                    "eliminated."))
            if line.eliminated:
                raise UserError(_(
                    "The line \"%s\" of account %s is already eliminated.",
                    line.account_name or line.account_code,
                    line.account_code))
            line.write({"eliminated": True, "debit": 0.0, "credit": 0.0})
            line.run_id.message_post(body=_(
                "Line of account %(code)s eliminated from the "
                "consolidation.", code=line.account_code))
        return True
