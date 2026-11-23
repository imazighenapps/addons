# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EscrowDeposit(models.Model):
    _name = "escrow.deposit.desk"
    _description = "Compte séquestre"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one("res.partner", string="Partie / Client")
    amount = fields.Monetary(string="Montant séquestré", required=True)
    released_amount = fields.Monetary(string="Montant libéré", default=0.0)
    remaining_amount = fields.Monetary(string="Solde séquestre", compute="_compute_remaining", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    condition_text = fields.Text(string="Conditions de débloquage")
    release_count = fields.Integer(string="Libérations", compute="_compute_remaining", store=True)
    state = fields.Selection([("draft","Brouillon"),("held","Séquestré"),("partial","Partiellement libéré"),("released","Libéré"),("cancelled","Annulé")], default="draft", tracking=True)
    notes = fields.Text(string="Notes / justificatifs")

    @api.depends("amount", "released_amount")
    def _compute_remaining(self):
        for rec in self:
            rec.remaining_amount = (rec.amount or 0.0) - (rec.released_amount or 0.0)
            rec.release_count = 1 if rec.released_amount else 0

    def action_hold(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("escrow.deposit.desk") or "ESC"
            rec.state = "held"

    def action_release_partial(self, amount=None):
        # callable from UI by setting released_amount then action
        for rec in self:
            if rec.remaining_amount <= 0:
                raise UserError(_("Aucun solde à libérer."))
            rec.state = "partial" if rec.remaining_amount > 0 else "released"

    def action_release_all(self):
        for rec in self:
            rec.released_amount = rec.amount
            rec.state = "released"

    def action_cancel(self):
        self.write({"state": "cancelled"})
