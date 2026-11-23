# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class BankLoan(models.Model):
    _name = "bank.loan"
    _description = "Emprunt bancaire"
    _inherit = ["mail.thread"]
    _order = "start_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one("res.partner", string="Banque / prêteur")
    principal_amount = fields.Monetary(string="Capital emprunté", required=True)
    interest_rate = fields.Float(string="Taux annuel (%)", required=True)
    insurance_rate = fields.Float(string="Assurance annuelle (%)", default=0.0)
    fees_amount = fields.Monetary(string="Frais de dossier")
    term_months = fields.Integer(string="Durée (mois)", required=True)
    start_date = fields.Date(string="Date de début", required=True, default=fields.Date.context_today)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    line_ids = fields.One2many("bank.loan.line", "loan_id", string="Échéancier")
    total_interest = fields.Monetary(string="Total intérêts", compute="_compute_totals", store=True)
    total_insurance = fields.Monetary(string="Total assurance", compute="_compute_totals", store=True)
    remaining_capital = fields.Monetary(string="Capital restant dû", compute="_compute_totals", store=True)
    accrued_interest = fields.Monetary(string="Intérêts courus (provision)", compute="_compute_totals", store=True)
    state = fields.Selection([("draft","Brouillon"),("running","En cours"),("closed","Clôturé"),("early","Clôturé anticipé")], default="draft", tracking=True)
    early_penalty = fields.Monetary(string="Pénalités clôture anticipée")
    notes = fields.Text(string="Notes")

    @api.depends("line_ids.interest_amount", "line_ids.insurance_amount", "line_ids.capital_amount", "line_ids.state")
    def _compute_totals(self):
        for rec in self:
            lines = rec.line_ids
            rec.total_interest = sum(lines.mapped("interest_amount"))
            rec.total_insurance = sum(lines.mapped("insurance_amount"))
            paid_capital = sum(lines.filtered(lambda l: l.state == "paid").mapped("capital_amount"))
            rec.remaining_capital = (rec.principal_amount or 0.0) - paid_capital
            # provision simple: intérêts des échéances non payées à venir sur le mois courant
            rec.accrued_interest = sum(lines.filtered(lambda l: l.state != "paid").mapped("interest_amount")) / max(rec.term_months or 1, 1)

    @api.constrains("principal_amount", "term_months")
    def _check_values(self):
        for rec in self:
            if rec.principal_amount <= 0 or rec.term_months <= 0:
                raise ValidationError(_("Le capital et la durée doivent être positifs."))

    def action_generate_schedule(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("bank.loan") or "LOAN"
            rec.line_ids.unlink()
            remaining = rec.principal_amount
            monthly_capital = rec.principal_amount / rec.term_months
            monthly_rate = (rec.interest_rate or 0.0) / 100.0 / 12.0
            monthly_ins = (rec.principal_amount * (rec.insurance_rate or 0.0) / 100.0) / 12.0
            vals = []
            for i in range(1, rec.term_months + 1):
                d = rec.start_date + relativedelta(months=+i)
                interest = remaining * monthly_rate
                cap = monthly_capital if i < rec.term_months else remaining
                vals.append((0, 0, {
                    "sequence": i, "due_date": d, "capital_amount": cap,
                    "interest_amount": interest, "insurance_amount": monthly_ins,
                }))
                remaining -= cap
            rec.line_ids = vals
            rec.state = "running"

    def action_mark_paid_next(self):
        for rec in self:
            line = rec.line_ids.filtered(lambda l: l.state == "due")[:1]
            if not line:
                raise UserError(_("Aucune échéance à marquer payée."))
            line.state = "paid"

    def action_close(self):
        self.write({"state": "closed"})

    def action_close_early(self):
        self.write({"state": "early"})
