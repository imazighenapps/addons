# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EhsIncident(models.Model):
    _name = "ehs.incident"
    _description = "EHS Incident"
    _inherit = ["mail.thread"]
    _order = "date_incident desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("INC %s")
        % fields.Datetime.now().strftime("%Y-%m-%d %H:%M"),
        help="Reference of the incident, generated at the report.")
    title = fields.Char(required=True, tracking=True)
    date_incident = fields.Date(
        string="Date", required=True, default=fields.Date.context_today,
        tracking=True)
    type = fields.Selection(
        [("injury", "Injury"), ("near_miss", "Near Miss"),
         ("property", "Property Damage"), ("environment", "Environment"),
         ("other", "Other")],
        default="near_miss", required=True, tracking=True,
        help="What kind of event was reported.")
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"),
         ("critical", "Critical")],
        default="low", required=True, tracking=True)
    location = fields.Char(
        help="Where it happened, for example Warehouse 2, loading bay.")
    reported_by = fields.Many2one(
        "res.users", string="Reported By", required=True,
        default=lambda self: self.env.user)
    involved_name = fields.Char(
        string="Involved Person",
        help="Name of the person involved, kept as free text.")
    description = fields.Text(tracking=True)
    immediate_action = fields.Text(
        string="Immediate Action",
        help="What was done on the spot, before the investigation.")
    action_ids = fields.One2many(
        "ehs.action", "incident_id", string="Corrective Actions")
    open_action_count = fields.Integer(
        string="Open Actions", compute="_compute_actions")
    total_action_count = fields.Integer(
        string="Total Actions", compute="_compute_actions")
    state = fields.Selection(
        [("draft", "Draft"), ("investigating", "Investigating"),
         ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    closed_date = fields.Date(readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("action_ids.state")
    def _compute_actions(self):
        for incident in self:
            incident.total_action_count = len(incident.action_ids)
            incident.open_action_count = len(
                incident.action_ids.filtered(
                    lambda action: action.state == "todo"))

    def action_investigate(self):
        for incident in self:
            if incident.state != "draft":
                raise UserError(_(
                    "Only a new incident can enter the investigation."))
            incident.state = "investigating"
            incident.message_post(body=_(
                "The investigation of the incident has started."))
        return True

    def action_close(self):
        for incident in self:
            if incident.state == "closed":
                raise UserError(_(
                    "Incident \"%s\" is already closed.", incident.title))
            if incident.state == "draft":
                raise UserError(_(
                    "Investigate incident \"%s\" before closing it.",
                    incident.title))
            if incident.open_action_count:
                raise UserError(_(
                    "Incident \"%s\" still has %s corrective action(s) to "
                    "do.", incident.title, incident.open_action_count))
            incident.write({
                "state": "closed",
                "closed_date": fields.Date.context_today(incident),
            })
            incident.message_post(body=_(
                "The incident is closed with all corrective actions done."))
        return True

    def action_reopen(self):
        for incident in self:
            incident.write({"state": "investigating", "closed_date": False})
            incident.message_post(body=_("The incident has been reopened."))
        return True
