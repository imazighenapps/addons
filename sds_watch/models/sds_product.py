# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SdsProduct(models.Model):
    _name = "sds.product"
    _description = "Chemical Product SDS"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    supplier = fields.Char(
        help="Supplier or manufacturer of the chemical product.")
    hazard_class = fields.Selection(
        [("flammable", "Flammable"), ("corrosive", "Corrosive"),
         ("toxic", "Toxic"), ("oxidizer", "Oxidizer"),
         ("irritant", "Irritant"), ("environment", "Environmental"),
         ("other", "Other")],
        default="other", required=True,
        help="Main hazard classification of the product.")
    current_issue = fields.Date(
        string="Current Issue Date", tracking=True,
        help="Issue date of the current safety data sheet.")
    current_expiry = fields.Date(
        string="Current Expiry Date", tracking=True,
        help="Expiry date of the current safety data sheet.")
    is_lapsed = fields.Boolean(
        string="Lapsed", compute="_compute_lapsed", store=True,
        help="True when the current sheet has expired.")
    is_missing = fields.Boolean(
        string="Missing Sheet", compute="_compute_lapsed", store=True,
        help="True when no current sheet dates are set.")
    version_ids = fields.One2many(
        "sds.version", "product_id", string="Sheet Versions", copy=False)
    version_count = fields.Integer(
        string="Versions", compute="_compute_version_count", store=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("current_issue", "current_expiry")
    def _compute_lapsed(self):
        today = fields.Date.context_today(self)
        for product in self:
            missing = not (product.current_issue and product.current_expiry)
            product.is_missing = missing
            product.is_lapsed = bool(
                not missing and product.current_expiry < today)

    @api.depends("version_ids")
    def _compute_version_count(self):
        for product in self:
            product.version_count = len(product.version_ids)

    @api.constrains("current_issue", "current_expiry")
    def _check_dates(self):
        for product in self:
            if product.current_issue and product.current_expiry \
                    and product.current_expiry < product.current_issue:
                raise ValidationError(_(
                    "The expiry date of the current sheet for %s cannot "
                    "come before its issue date.", product.name))
