# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItAsset(models.Model):
    _name = "it.asset"
    _description = "IT Asset"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    serial = fields.Char(
        string="Serial Number", tracking=True,
        help="Manufacturer serial number printed on the device.")
    model_name = fields.Char(string="Model")
    asset_type = fields.Selection(
        [("laptop", "Laptop"), ("phone", "Phone"), ("screen", "Screen"),
         ("tablet", "Tablet"), ("other", "Other")],
        default="laptop", required=True, tracking=True)
    purchase_on = fields.Date(string="Purchased On")
    state = fields.Selection(
        [("stock", "In Stock"), ("in_use", "In Use"),
         ("repair", "In Repair"), ("retired", "Retired")],
        default="stock", required=True, tracking=True, index=True)
    current_holder = fields.Char(
        string="Current Holder", compute="_compute_current_holder", store=True,
        help="Holder of the open assignment, if any.")
    assignment_ids = fields.One2many(
        "it.assignment", "asset_id", string="Assignments")
    assignment_count = fields.Integer(
        string="Assignments", compute="_compute_assignment_counts", store=True)
    open_assignment_count = fields.Integer(
        string="Open Assignments", compute="_compute_assignment_counts",
        store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("assignment_ids", "assignment_ids.state",
                 "assignment_ids.holder", "assignment_ids.assigned_on")
    def _compute_current_holder(self):
        for asset in self:
            open_assignment = asset.assignment_ids.filtered(
                lambda assignment: assignment.state == "open").sorted(
                key=lambda assignment: assignment.assigned_on or fields.Date.today(),
                reverse=True)[:1]
            asset.current_holder = open_assignment.holder if open_assignment else False

    @api.depends("assignment_ids", "assignment_ids.state")
    def _compute_assignment_counts(self):
        for asset in self:
            assignments = asset.assignment_ids
            asset.assignment_count = len(assignments)
            asset.open_assignment_count = len(assignments.filtered(
                lambda assignment: assignment.state == "open"))

    @api.constrains("serial", "company_id")
    def _check_serial_unique(self):
        for asset in self:
            if not asset.serial:
                continue
            duplicate = self.search([
                ("id", "!=", asset.id),
                ("serial", "=", asset.serial),
                ("company_id", "=", asset.company_id.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "The serial number \"%s\" is already used by asset "
                    "\"%s\" in the same company.",
                    asset.serial, duplicate.name))
