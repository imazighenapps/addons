# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestInspection(models.Model):
    _name = "pest.inspection"
    _description = "Pest Station Inspection"
    _inherit = ["mail.thread"]
    _order = "inspection_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Inspection %s")
        % fields.Date.context_today(self))
    station_id = fields.Many2one(
        "pest.station", string="Station", required=True,
        ondelete="cascade", index=True, tracking=True)
    inspection_date = fields.Date(
        string="Inspection Date", required=True,
        default=fields.Date.context_today, tracking=True)
    contractor = fields.Char(
        help="Contractor or technician who performed the visit.")
    result = fields.Selection(
        [("clear", "Clear"), ("activity", "Activity Found"),
         ("action", "Corrective Action")],
        default="clear", required=True, tracking=True)
    finding_state = fields.Selection(
        [("none", "No Finding"), ("open", "Open"), ("closed", "Closed")],
        default="none", required=True, copy=False, tracking=True, index=True)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Confirmed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    company_id = fields.Many2one(
        related="station_id.company_id", store=True, readonly=True)
    note = fields.Text()

    @api.constrains("inspection_date")
    def _check_date(self):
        for inspection in self:
            if inspection.inspection_date > fields.Date.context_today(inspection):
                raise ValidationError(_(
                    "The inspection date of %s cannot be in the future.",
                    inspection.name))

    @api.constrains("result", "finding_state")
    def _check_finding(self):
        for inspection in self:
            if inspection.result == "clear" and inspection.finding_state == "open":
                raise ValidationError(_(
                    "A clear inspection cannot have an open finding."))

    def action_confirm(self):
        for inspection in self:
            if inspection.state != "draft":
                raise UserError(
                    _("Only a draft inspection can be confirmed."))
            vals = {"state": "done"}
            if inspection.result != "clear" and inspection.finding_state == "none":
                vals["finding_state"] = "open"
            inspection.write(vals)
            inspection.station_id.write(
                {"last_check": inspection.inspection_date})
            inspection.message_post(body=_(
                "Inspection confirmed on %s.", inspection.inspection_date))
        return True

    def action_close_finding(self):
        for inspection in self:
            if inspection.finding_state != "open":
                raise UserError(_("Only an open finding can be closed."))
            inspection.write({"finding_state": "closed"})
            inspection.message_post(body=_("Finding closed."))
        return True
