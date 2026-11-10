# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AssetInventory(models.Model):
    _name = "asset.inventory"
    _description = "Asset Count Campaign"
    _inherit = ["mail.thread"]
    _order = "planned_date desc, id desc"

    name = fields.Char(
        required=True, copy=False, tracking=True,
        help="Reference of the count campaign.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", required=True, tracking=True,
        default=lambda self: self.env.user)
    planned_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"),
         ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    closed_on = fields.Date(readonly=True, copy=False)
    line_ids = fields.One2many(
        "asset.inventory.line", "inventory_id", string="Count Lines",
        copy=True)
    line_count = fields.Integer(
        string="Assets", compute="_compute_totals", store=True)
    found_count = fields.Integer(
        string="Found", compute="_compute_totals", store=True)
    missing_count = fields.Integer(
        string="Missing", compute="_compute_totals", store=True)
    moved_count = fields.Integer(
        string="Moved", compute="_compute_totals", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.result")
    def _compute_totals(self):
        for inventory in self:
            lines = inventory.line_ids
            inventory.line_count = len(lines)
            inventory.found_count = len(lines.filtered(
                lambda line: line.result == "found"))
            inventory.missing_count = len(lines.filtered(
                lambda line: line.result == "missing"))
            inventory.moved_count = len(lines.filtered(
                lambda line: line.result == "moved"))

    def _ensure_open(self):
        for inventory in self:
            if inventory.state == "closed":
                raise UserError(_(
                    "The closed campaign %s cannot be changed.", inventory.name))

    def write(self, vals):
        self._ensure_open()
        return super().write(vals)

    def action_start(self):
        for inventory in self:
            if inventory.state != "draft":
                raise UserError(_("Only a draft campaign can be started."))
            if not inventory.line_ids:
                raise UserError(_(
                    "Add at least one asset line before starting %s.",
                    inventory.name))
            inventory.state = "in_progress"
            inventory.message_post(body=_("Count campaign started."))
        return True

    def action_close(self):
        for inventory in self:
            if inventory.state != "in_progress":
                raise UserError(_("Only a campaign in progress can be closed."))
            pending = inventory.line_ids.filtered(lambda line: not line.result)
            if pending:
                raise UserError(_(
                    "Record a result for every asset before closing %s.",
                    inventory.name))
            inventory.write({
                "state": "closed",
                "closed_on": fields.Date.context_today(inventory),
            })
            inventory.message_post(body=_(
                "Campaign closed: %s found, %s missing, %s moved.",
                inventory.found_count, inventory.missing_count,
                inventory.moved_count))
        return True

    def action_reset(self):
        for inventory in self:
            if inventory.state != "in_progress":
                raise UserError(_(
                    "Only a campaign in progress can be reset to draft."))
            inventory.state = "draft"
            inventory.message_post(body=_("Campaign reset to draft."))
        return True
