# -*- coding: utf-8 -*-
from odoo import fields, models


class CleaningAgent(models.Model):
    _name = "cleaning.agent"
    _description = "Cleaning Agent"
    _order = "name"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Linked Contact")
    phone = fields.Char()
    email = fields.Char()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    hourly_rate = fields.Float(string="Hourly Rate")
    monthly_salary = fields.Float(string="Monthly Salary")
    active = fields.Boolean(default=True)
    visit_ids = fields.One2many("cleaning.visit", "agent_id", string="Visits")
    sites_count = fields.Integer(compute="_compute_stats")

    def _compute_stats(self):
        visits = self.env["cleaning.visit"].search([("agent_id", "in", self.ids)])
        sites = self.env["cleaning.site"].search([("agent_ids", "in", self.ids)])
        for agent in self:
            agent.sites_count = len(sites.filtered(
                lambda s: agent in s.agent_ids))
            agent.visit_ids = visits.filtered(lambda v: v.agent_id == agent)


class CleaningSite(models.Model):
    _name = "cleaning.site"
    _description = "Customer Site"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", required=True,
                                 ondelete="restrict")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    address = fields.Char()
    area = fields.Float(string="Area (m²)")
    area_uom_id = fields.Many2one(
        "uom.uom", default=lambda self: self.env.ref("uom.product_uom_square_meter"),
        string="Area Unit")
    price_per_m2 = fields.Float(string="Price per m²")
    price_per_visit = fields.Float(string="Price per Visit")
    billing_mode = fields.Selection(
        [("visit", "Per Visit"), ("area", "Per Square Metre")],
        default="visit", required=True)
    access_notes = fields.Text(string="Access & Security Notes")
    agent_ids = fields.Many2many("cleaning.agent", string="Assigned Agents")
    active = fields.Boolean(default=True)
    visit_count = fields.Integer(compute="_compute_stats")
    last_visit_date = fields.Datetime(compute="_compute_stats", store=True)

    def _compute_stats(self):
        visits = self.env["cleaning.visit"].search([("site_id", "in", self.ids)])
        for site in self:
            mine = visits.filtered(lambda v: v.site_id == site)
            site.visit_count = len(mine)
            latest = mine.sorted("check_in", reverse=True)[:1]
            site.last_visit_date = latest.check_in if latest else False

    def visit_price(self):
        """Price of one visit for this site."""
        self.ensure_one()
        if self.billing_mode == "area":
            return self.price_per_m2 * (self.area or 0.0)
        return self.price_per_visit