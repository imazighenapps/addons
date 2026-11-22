# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class JpQualifyingInvoice(models.Model):
    _name = "jp.qualifying.invoice"
    _description = "Facture qualifiante Japon"
    _inherit = ["mail.thread"]
    _order = "invoice_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one("account.move", string="Facture", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    invoice_date = fields.Date(related="invoice_id.invoice_date", store=True)
    registration_number = fields.Char(string="Numéro d'enregistrement (T+13)", required=True)
    consumption_tax_rate = fields.Float(string="Taux de taxe (%)", default=10.0)
    taxable_amount = fields.Monetary(string="Montant taxable", compute="_compute_amounts", store=True)
    tax_amount = fields.Monetary(string="Montant taxe", compute="_compute_amounts", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    compliance_ok = fields.Boolean(string="Conforme", compute="_compute_compliance", store=True)
    state = fields.Selection([("draft","Brouillon"),("registered","Enregistrée"),("compliant","Conforme")], default="draft", tracking=True)
    notes = fields.Text(string="Notes / journal")

    _sql_constraints = [("jp_qi_invoice_uniq", "unique(invoice_id)", "Un enregistrement existe déjà pour cette facture.")]

    @api.depends("invoice_id.amount_untaxed", "invoice_id.amount_tax")
    def _compute_amounts(self):
        for rec in self:
            rec.taxable_amount = rec.invoice_id.amount_untaxed
            rec.tax_amount = rec.invoice_id.amount_tax

    @api.depends("registration_number", "invoice_id")
    def _compute_compliance(self):
        for rec in self:
            reg = (rec.registration_number or "").strip()
            rec.compliance_ok = reg.startswith("T") and len(reg) == 14 and reg[1:].isdigit() and bool(rec.invoice_id)

    @api.constrains("registration_number")
    def _check_registration(self):
        for rec in self:
            reg = (rec.registration_number or "").strip()
            if reg and not (reg.startswith("T") and len(reg) == 14 and reg[1:].isdigit()):
                raise ValidationError(_("Le numéro d'enregistrement doit être au format T + 13 chiffres."))

    def action_register(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("jp.qualifying.invoice") or "JPQI"
            if not rec.compliance_ok:
                raise UserError(_("Complétez un numéro d'enregistrement valide (T+13 chiffres)."))
            rec.state = "registered"

    def action_mark_compliant(self):
        for rec in self:
            if not rec.compliance_ok:
                raise UserError(_("Contrôles de complétude non satisfaits."))
            rec.state = "compliant"
            rec.notes = ((rec.notes or "") + "\n[%s] %s" % (fields.Datetime.now(), _("Marqué conforme."))).strip()
