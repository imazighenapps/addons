# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CustomerFeedbackTopic(models.Model):
    _name = "customer.feedback.topic"
    _description = "Feedback Topic"
    _order = "name, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "A feedback topic with this name already exists for this company."),
    ]


class CustomerFeedback(models.Model):
    _name = "customer.feedback"
    _description = "Customer Feedback"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True,
        tracking=True)
    contact_name = fields.Char(string="Contact Person")
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    channel = fields.Selection(
        [("email", "Email"), ("phone", "Phone"), ("meeting", "Meeting"),
         ("web", "Web"), ("other", "Other")],
        string="Channel", default="email", required=True)
    score = fields.Selection(
        [("1", "1 - Very Dissatisfied"), ("2", "2 - Dissatisfied"),
         ("3", "3 - Neutral"), ("4", "4 - Satisfied"),
         ("5", "5 - Very Satisfied")],
        string="Satisfaction", required=True, tracking=True, index=True)
    topic_id = fields.Many2one(
        "customer.feedback.topic", string="Topic", tracking=True)
    order_id = fields.Many2one(
        "sale.order", string="Sale Order", tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    state = fields.Selection(
        [("new", "New"), ("progress", "In Progress"), ("done", "Done")],
        default="new", required=True, tracking=True, index=True)
    comment = fields.Text(string="Customer Comment")
    resolution = fields.Text(string="Resolution / Follow-up Note")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("customer.feedback")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Customer Feedback",
                        "code": "customer.feedback",
                        "prefix": "CFB/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_progress(self):
        for rec in self:
            rec.state = "progress"

    def action_done(self):
        for rec in self:
            rec.state = "done"

    def action_reset(self):
        for rec in self:
            rec.state = "new"
