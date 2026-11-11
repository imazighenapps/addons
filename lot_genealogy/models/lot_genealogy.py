# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LotGenealogy(models.Model):
    _name = "lot.genealogy"
    _description = "Lot Genealogy"
    _inherit = ["mail.thread"]
    _order = "produced_on desc, id desc"

    name = fields.Char(string="Lot Reference", required=True, tracking=True)
    product_name = fields.Char(string="Product", required=True, tracking=True)
    produced_on = fields.Date(string="Produced On", required=True,
                              default=fields.Date.context_today, tracking=True)
    impacted = fields.Boolean(
        string="Impacted", default=False, tracking=True,
        help="Marked when this lot is affected by a quality issue.")
    parent_link_ids = fields.One2many(
        "lot.genealogy.link", "child_lot_id", string="Parent Links")
    child_link_ids = fields.One2many(
        "lot.genealogy.link", "parent_lot_id", string="Child Links")
    parent_count = fields.Integer(compute="_compute_counts", store=True)
    child_count = fields.Integer(compute="_compute_counts", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("parent_link_ids", "child_link_ids")
    def _compute_counts(self):
        for lot in self:
            lot.parent_count = len(lot.parent_link_ids)
            lot.child_count = len(lot.child_link_ids)

    @api.constrains("name", "company_id")
    def _check_name_company(self):
        for lot in self:
            if not lot.name or not lot.company_id:
                continue
            dup = self.search_count([
                ("name", "=", lot.name),
                ("company_id", "=", lot.company_id.id),
                ("id", "!=", lot.id),
            ])
            if dup:
                raise ValidationError(_(
                    "The lot reference must be unique per company."))

    def action_mark_impacted(self):
        for lot in self:
            lot.impacted = True
            lot.message_post(body=_("The lot was marked as impacted."))
        return True

    def action_clear_impacted(self):
        for lot in self:
            lot.impacted = False
            lot.message_post(body=_("The impacted flag was cleared."))
        return True
