# -*- coding: utf-8 -*-
from odoo import fields, models, _


class VisitorPurgeWizard(models.TransientModel):
    _name = "visitor.purge.wizard"
    _description = "Purge the Visitor Log"

    name = fields.Char(
        required=True, default=lambda self: _("Register purge"),
        help="Reason of the purge, kept for the operator's own record.")
    date_limit = fields.Date(
        string="Delete Visits Before", required=True,
        default=fields.Date.context_today,
        help="Visits checked out before this date are deleted from the "
             "register of the current company.")

    def action_purge(self):
        self.ensure_one()
        limit = fields.Datetime.to_datetime(self.date_limit)
        visits = self.env["visitor.log"].search([
            ("state", "=", "checked_out"),
            ("check_out", "<", limit),
            ("company_id", "=", self.env.company.id),
        ])
        visits.unlink()
        return True
