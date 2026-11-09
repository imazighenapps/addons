# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class QualityClaim(models.Model):
    _name = "quality.claim"
    _description = "Quality Claim"
    _inherit = ["mail.thread"]
    _order = "date_claim desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _(
            "Claim %s", fields.Date.context_today(self)))
    claim_type = fields.Selection(
        [("customer", "Customer"), ("supplier", "Supplier"),
         ("internal", "Internal")],
        string="Claim Type", required=True, default="customer",
        tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, tracking=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, tracking=True)
    lot_ref = fields.Char(
        string="Lot / Serial",
        help="Lot or serial number of the product the claim is about.")
    quantity = fields.Float(default=1.0, required=True)
    defect_code = fields.Selection(
        [("dimensional", "Dimensional"), ("surface", "Surface"),
         ("function", "Function"), ("packaging", "Packaging"),
         ("documentation", "Documentation"), ("other", "Other")],
        string="Defect", default="other", required=True)
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        default="major", required=True, tracking=True)
    date_claim = fields.Date(
        string="Claim Date", required=True,
        default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"),
         ("investigation", "Investigation"), ("action", "Action Plan"),
         ("done", "Done"), ("refused", "Refused")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    root_cause = fields.Text(string="Root Cause")
    cost_amount = fields.Monetary(
        string="Claim Cost", currency_field="currency_id",
        default=0.0, tracking=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company,
        required=True, index=True)
    action_ids = fields.One2many(
        "quality.claim.action", "claim_id", string="Corrective Actions",
        copy=True)
    action_count = fields.Integer(
        string="Actions", compute="_compute_action_counts")
    action_done_count = fields.Integer(
        string="Actions Done", compute="_compute_action_counts")
    note = fields.Text()

    @api.depends("action_ids", "action_ids.state")
    def _compute_action_counts(self):
        for claim in self:
            claim.action_count = len(claim.action_ids)
            claim.action_done_count = len(claim.action_ids.filtered(
                lambda action: action.state == "done"))

    @api.constrains("quantity")
    def _check_quantity(self):
        for claim in self:
            if claim.quantity <= 0:
                raise ValidationError(_(
                    "The claimed quantity must be greater than zero."))

    @api.constrains("cost_amount")
    def _check_cost(self):
        for claim in self:
            if claim.cost_amount < 0:
                raise ValidationError(_(
                    "The cost of the claim cannot be negative."))

    def action_open(self):
        for claim in self:
            if claim.state != "draft":
                raise UserError(_(
                    "Only a draft claim can be opened."))
            claim.state = "open"
            claim.message_post(body=_(
                "Claim opened for analysis (%(type)s).",
                type=claim.claim_type))
        return True

    def action_investigate(self):
        for claim in self:
            if claim.state != "open":
                raise UserError(_(
                    "Only an open claim can move to investigation."))
            claim.state = "investigation"
            claim.message_post(body=_(
                "Claim handed over to the quality investigation."))
        return True

    def action_plan(self):
        for claim in self:
            if claim.state != "investigation":
                raise UserError(_(
                    "A claim can only be planned from the investigation "
                    "stage."))
            if not (claim.root_cause or "").strip():
                raise UserError(_(
                    "Fill in the root cause before planning the corrective "
                    "actions of the claim \"%s\".", claim.name))
            claim.state = "action"
            claim.message_post(body=_(
                "Root cause recorded, corrective actions may be planned."))
        return True

    def action_close(self):
        for claim in self:
            if claim.state != "action":
                raise UserError(_(
                    "Only a claim under action plan can be closed."))
            pending = claim.action_ids.filtered(
                lambda action: action.state == "todo")
            if pending:
                raise UserError(_(
                    "The claim \"%(name)s\" cannot be closed: %(count)s "
                    "corrective action(s) are still open.",
                    name=claim.name, count=len(pending)))
            claim.state = "done"
            claim.message_post(body=_(
                "Claim closed with %(count)s corrective action(s).",
                count=len(claim.action_ids)))
        return True

    def action_refuse(self):
        for claim in self:
            if claim.state == "done":
                raise UserError(_(
                    "The claim \"%s\" is already closed and can no longer be "
                    "refused.", claim.name))
            claim.state = "refused"
            claim.message_post(body=_("Claim refused and filed."))
        return True

    def action_reset(self):
        for claim in self:
            if claim.state != "draft":
                claim.state = "draft"
                claim.message_post(body=_("Claim reset to draft."))
        return True


class QualityClaimAction(models.Model):
    _name = "quality.claim.action"
    _description = "Quality Claim Corrective Action"
    _order = "claim_id, sequence, id"

    claim_id = fields.Many2one(
        "quality.claim", string="Claim", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(
        string="Action", required=True,
        help="What has to be done to fix the root cause.")
    user_id = fields.Many2one(
        "res.users", string="Responsible", required=True,
        default=lambda self: self.env.user)
    due_date = fields.Date()
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Done")],
        default="todo", required=True, index=True)
    done_date = fields.Date(string="Done On")

    def action_done(self):
        for action in self:
            if action.state == "done":
                raise UserError(_(
                    "The corrective action \"%s\" is already done.",
                    action.name))
            action.state = "done"
            action.done_date = fields.Date.context_today(action)
        return True

    def action_reopen(self):
        for action in self:
            if action.state != "done":
                raise UserError(_(
                    "Only a done corrective action can be reopened."))
            action.state = "todo"
            action.done_date = False
        return True
