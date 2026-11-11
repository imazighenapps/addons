# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CanteenCount(models.Model):
    _name = "canteen.count"
    _description = "Canteen Headcount"
    _inherit = ["mail.thread"]
    _order = "meal_date desc, team_name"

    name = fields.Char(
        required=True,
        default=lambda self: _("Canteen %s")
        % fields.Date.context_today(self),
        help="Reference of the headcount, generated at creation.")
    meal_date = fields.Date(
        string="Meal Date", required=True,
        default=fields.Date.context_today, tracking=True, index=True)
    team_name = fields.Char(
        string="Team", required=True, tracking=True,
        help="Team or department ordering the meals.")
    employee_id = fields.Many2one(
        "hr.employee", string="Responsible", required=True, tracking=True,
        help="Employee who reports the headcount for the team.")
    meal_count = fields.Integer(
        string="Meals", default=1, required=True, tracking=True,
        help="Number of lunches ordered for the team.")
    cutoff_time = fields.Float(
        string="Cut-off Time", default=10.0, required=True,
        help="Hour after which the count is closed, in 24h format.")
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    sent_on = fields.Date(
        string="Sent On", readonly=True, copy=False, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.constrains("meal_count")
    def _check_meal_count(self):
        for record in self:
            if record.meal_count <= 0:
                raise ValidationError(_(
                    "The number of meals for %s must be above zero.",
                    record.team_name))

    @api.constrains("cutoff_time")
    def _check_cutoff_time(self):
        for record in self:
            if record.cutoff_time < 0.0 or record.cutoff_time >= 24.0:
                raise ValidationError(_(
                    "The cut-off time for %s must be between 0:00 and "
                    "23:59.", record.team_name))

    def action_send(self):
        for record in self:
            if record.state != "draft":
                raise ValidationError(_(
                    "The headcount for %s is already sent.",
                    record.team_name))
            record.write({
                "state": "sent",
                "sent_on": fields.Date.context_today(record),
            })
            record.message_post(body=_(
                "The headcount was sent to the caterer."))
        return True
