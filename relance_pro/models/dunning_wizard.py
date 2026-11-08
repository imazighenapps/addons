# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DunningRunWizard(models.TransientModel):
    _name = "dunning.run.wizard"
    _description = "Run Dunning"

    date_ref = fields.Date(
        required=True, default=fields.Date.context_today)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    partner_ids = fields.Many2many(
        "res.partner", string="Customers",
        help="Leave empty to chase every customer of the company.")
    dry_run = fields.Boolean(
        string="Dry Run",
        help="Create the lines but do not send any email.")

    def _paused(self, partner):
        if partner.dunning_paused:
            return True
        return bool(partner.dunning_pause_until
                    and partner.dunning_pause_until >= self.date_ref)

    def action_run(self):
        self.ensure_one()
        Move = self.env["account.move"].sudo()
        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("invoice_date_due", "<", self.date_ref),
            ("company_id", "=", self.company_id.id),
        ]
        if self.partner_ids:
            domain.append(("partner_id", "in", self.partner_ids.ids))
        moves = Move.search(domain)
        levels = self.env["dunning.level"].sudo().search([
            ("company_id", "=", self.company_id.id),
            ("active", "=", True),
        ], order="day_offset desc")
        Line = self.env["dunning.line"]
        created = Line
        for move in moves:
            if self._paused(move.partner_id):
                continue
            days = (self.date_ref - move.invoice_date_due).days
            level = levels.filtered(
                lambda lvl: lvl.day_offset <= days)[:1]
            if not level:
                continue
            if Line.search_count([
                    ("move_id", "=", move.id),
                    ("level_id", "=", level.id)]):
                continue
            line = Line.create({
                "partner_id": move.partner_id.id,
                "move_id": move.id,
                "level_id": level.id,
                "company_id": self.company_id.id,
                "fee_amount": level.fee_amount,
            })
            if not self.dry_run:
                line.action_send()
            created |= line
        action = {
            "type": "ir.actions.act_window",
            "name": _("Dunning Lines"),
            "res_model": "dunning.line",
            "view_mode": "list,form",
        }
        if created:
            action["domain"] = [("id", "in", created.ids)]
        else:
            action["domain"] = [
                ("company_id", "=", self.company_id.id),
                ("state", "=", "draft"),
            ]
        return action
