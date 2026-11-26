# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


REPORT_TYPES = [
    ("pl", "Profit and Loss"),
    ("bs", "Balance Sheet"),
    ("cashflow", "Cash Flow"),
    ("trial_balance", "Trial Balance"),
    ("custom", "Custom"),
]

LINE_TYPES = [
    ("title", "Section Title"),
    ("line", "Account Line"),
    ("subtotal", "Subtotal"),
]


class FrReport(models.Model):
    _name = "fr.report"
    _description = "Financial Report Definition"
    _order = "sequence, id"

    name = fields.Char(string="Report Name", required=True, translate=True)
    sequence = fields.Integer(default=10)
    report_type = fields.Selection(REPORT_TYPES, string="Report Type", required=True, default="custom")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company)
    line_ids = fields.One2many("fr.report.line", "report_id", string="Lines", copy=True)
    note = fields.Text(string="Notes")

    def action_open_wizard(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        return {
            "type": "ir.actions.act_window",
            "name": _("Generate Financial Report"),
            "res_model": "fr.report.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_report_id": self.id,
                "default_company_id": self.company_id.id or self.env.company.id,
                "default_date_from": today.replace(month=1, day=1),
                "default_date_to": today,
            },
        }


class FrReportLine(models.Model):
    _name = "fr.report.line"
    _description = "Financial Report Line"
    _order = "sequence, id"

    report_id = fields.Many2one("fr.report", string="Report", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    code = fields.Char(string="Code")
    name = fields.Char(string="Label", required=True, translate=True)
    line_type = fields.Selection(LINE_TYPES, string="Line Type", required=True, default="line")
    parent_id = fields.Many2one(
        "fr.report.line", string="Parent Section",
        domain="[('id', '!=', id), ('report_id', '=', report_id), ('line_type', 'in', ('title', 'subtotal'))]")
    sign = fields.Selection([
        ("1", "Credit - Debit"),
        ("-1", "Debit - Credit"),
    ], string="Balance Sign", default="1", required=True)
    invert = fields.Boolean(string="Invert Sign")
    internal_group = fields.Selection([
        ("equity", "Equity"),
        ("asset", "Assets"),
        ("liability", "Liabilities"),
        ("income", "Income"),
        ("expense", "Expenses"),
        ("off_balance", "Off Balance"),
    ], string="Account Internal Group")
    account_ids = fields.Many2many("account.account", string="Accounts")
    code_prefixes = fields.Char(
        string="Account Code Prefixes",
        help="Comma-separated account code prefixes, for example: 6,70,71")

    @api.constrains("code_prefixes")
    def _check_code_prefixes(self):
        for line in self:
            if not line.code_prefixes:
                continue
            for part in line.code_prefixes.split(","):
                part = part.strip()
                if part and not part.replace(".", "").isdigit():
                    raise UserError(_("Invalid account prefix '%s'. Use numeric prefixes separated by commas.") % part)

    @api.constrains("line_type", "internal_group", "account_ids", "code_prefixes")
    def _check_line_source(self):
        for line in self:
            if line.line_type != "line":
                continue
            has_source = bool(line.internal_group or line.account_ids or line.code_prefixes)
            if not has_source:
                raise UserError(_("Line '%s' must define accounts using an internal group, explicit accounts, or code prefixes.") % line.name)
            if line.internal_group and (line.account_ids or line.code_prefixes):
                raise UserError(_("Line '%s' must use only one account source: internal group, explicit accounts, or code prefixes.") % line.name)

    def _get_account_domain(self):
        self.ensure_one()
        if self.internal_group:
            return [("internal_group", "=", self.internal_group)]
        if self.account_ids:
            return [("id", "in", self.account_ids.ids)]
        if self.code_prefixes:
            prefixes = [p.strip() for p in self.code_prefixes.split(",") if p.strip()]
            if not prefixes:
                return [("id", "=", 0)]
            domain = ["|"] * (len(prefixes) - 1)
            for prefix in prefixes:
                domain.append(("code", "=like", prefix + "%"))
            return domain
        return [("id", "=", 0)]
