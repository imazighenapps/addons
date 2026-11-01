# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ApprovalDeskRequest(models.Model):
    _name = "approval.desk.request"
    _description = "Approval Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True,
        help="Reference of the request, generated from the APR/ sequence.")
    model_name = fields.Char(
        string="Document Model", tracking=True,
        help="Technical name of the model of the record to approve, for "
             "example res.partner or account.move.")
    res_id = fields.Integer(string="Document ID", tracking=True)
    res_name = fields.Char(
        string="Document", tracking=True,
        help="Readable name of the record being approved, kept as a snapshot "
             "so the request stays meaningful even if the record changes.")
    amount = fields.Monetary(
        currency_field="currency_id", tracking=True,
        help="Amount submitted to the approval chain. It selects the "
             "approvers whose threshold is reached.")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    requester_id = fields.Many2one(
        "res.users", string="Requester", required=True, tracking=True,
        default=lambda self: self.env.user)
    state = fields.Selection(
        [("draft", "Draft"), ("waiting", "Waiting Approval"),
         ("approved", "Approved"), ("refused", "Refused")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    step_ids = fields.One2many(
        "approval.desk.step", "request_id", string="Approval Steps",
        copy=True)
    current_step = fields.Many2one(
        "approval.desk.step", string="Current Step",
        compute="_compute_current_step",
        help="First pending step of the chain: the one that must sign now.")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "The approval request reference must be unique per company."),
        ('amount_positive', "CHECK(amount >= 0)", "The amount of an approval request cannot be negative."),
    ]


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "approval.desk.request") or "/"
        return super().create(vals_list)

    @api.depends("step_ids.state", "step_ids.sequence")
    def _compute_current_step(self):
        for request in self:
            pending = request.step_ids.filtered(
                lambda step: step.state == "pending")
            request.current_step = pending.sorted(
                lambda step: (step.sequence, step.id))[:1]

    @api.constrains("model_name", "res_id")
    def _check_document(self):
        for request in self:
            if request.res_id and not request.model_name:
                raise ValidationError(_(
                    "Set the document model when a document ID is given."))

    def _pending_step(self):
        """Return the first pending step of the chain, if any."""
        self.ensure_one()
        return self.env["approval.desk.step"].search([
            ("request_id", "=", self.id),
            ("state", "=", "pending"),
        ], order="sequence, id", limit=1)

    def action_submit(self):
        for request in self:
            if request.state != "draft":
                raise UserError(_(
                    "Only a draft request can be submitted for approval."))
            candidates = request.step_ids.filtered("approver_id")
            if not candidates:
                raise UserError(_(
                    "Add at least one approver with a minimum amount before "
                    "submitting the request."))
            selected = {}
            for step in candidates.sorted(
                    lambda step: (step.min_amount, step.sequence, step.id)):
                if request.amount >= step.min_amount:
                    selected[step.approver_id.id] = step
            if not selected:
                raise UserError(_(
                    "No approver matches the amount %(amount).2f "
                    "%(currency)s. Lower a threshold or add an approver.",
                    amount=request.amount,
                    currency=request.currency_id.name))
            keep = self.env["approval.desk.step"]
            for step in selected.values():
                keep |= step
            (request.step_ids - keep).unlink()
            ordered = keep.sorted(
                lambda step: (step.min_amount, step.sequence, step.id))
            for index, step in enumerate(ordered, start=1):
                step.sequence = index * 10
            request.write({"state": "waiting"})
            request.message_post(body=_(
                "Request submitted for %(count)s approval step(s), first "
                "approver: %(approver)s.",
                count=len(ordered),
                approver=ordered[0].approver_id.name))
        return True

    def action_approve(self):
        for request in self:
            if request.state != "waiting":
                raise UserError(_(
                    "Only a request waiting for approval can be approved."))
            step = request._pending_step()
            if not step:
                raise UserError(_(
                    "This request has no pending approval step."))
            if step.approver_id != self.env.user:
                raise UserError(_(
                    "Step %(sequence)s of this request must be approved by "
                    "%(approver)s, not by %(user)s.",
                    sequence=step.sequence,
                    approver=step.approver_id.name,
                    user=self.env.user.name))
            step.write({
                "state": "approved",
                "decision_date": fields.Datetime.now(),
            })
            next_step = request._pending_step()
            if next_step:
                request.message_post(body=_(
                    "Step %(sequence)s approved by %(approver)s. Next "
                    "approver: %(next)s.",
                    sequence=step.sequence,
                    approver=self.env.user.name,
                    next=next_step.approver_id.name))
            else:
                request.write({"state": "approved"})
                request.message_post(body=_(
                    "Request approved by %s.", self.env.user.name))
        return True

    def action_refuse(self):
        for request in self:
            if request.state not in ("draft", "waiting"):
                raise UserError(_(
                    "Only a draft or waiting request can be refused."))
            step = self.env["approval.desk.step"]
            if request.state == "waiting":
                step = request._pending_step()
            if step:
                allowed = step.approver_id | request.requester_id
                if self.env.user not in allowed:
                    raise UserError(_(
                        "Only %(approver)s or the requester can refuse this "
                        "request.",
                        approver=step.approver_id.name))
                step.write({
                    "state": "refused",
                    "decision_date": fields.Datetime.now(),
                })
            request.write({"state": "refused"})
            request.message_post(body=_(
                "Request refused by %s.", self.env.user.name))
        return True

    def action_reset(self):
        for request in self:
            if request.state == "draft":
                raise UserError(_("This request is already in draft."))
            request.step_ids.unlink()
            request.write({"state": "draft"})
            request.message_post(body=_(
                "Request reset to draft: the approval steps were cleared."))
        return True


class ApprovalDeskStep(models.Model):
    _name = "approval.desk.step"
    _description = "Approval Step"
    _inherit = ["mail.thread"]
    _order = "request_id, sequence, id"

    request_id = fields.Many2one(
        "approval.desk.request", string="Request", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    approver_id = fields.Many2one(
        "res.users", string="Approver", required=True, tracking=True)
    min_amount = fields.Monetary(
        string="Minimum Amount", currency_field="currency_id",
        help="The step applies when the request amount reaches this value.")
    currency_id = fields.Many2one(
        related="request_id.currency_id", store=True, readonly=True)
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"),
         ("refused", "Refused")],
        default="pending", required=True, tracking=True, index=True)
    decision_date = fields.Datetime(readonly=True, tracking=True)
    comment = fields.Text(tracking=True)

    _sql_constraints = [
        ('min_amount_positive', "CHECK(min_amount >= 0)", "The minimum amount of an approval step cannot be negative."),
        ('request_approver_uniq', "UNIQUE(request_id, approver_id)", "An approver can only appear once in the approval chain."),
    ]


    @api.model_create_multi
    def create(self, vals_list):
        request_ids = {vals["request_id"] for vals in vals_list
                       if vals.get("request_id")}
        if request_ids:
            locked = self.env["approval.desk.request"].browse(
                sorted(request_ids)).filtered(
                    lambda request: request.state != "draft")
            if locked:
                raise UserError(_(
                    "The approval chain of \"%s\" is already submitted. "
                    "Reset the request to draft first.", locked[0].name))
        return super().create(vals_list)

    def action_approve(self):
        self.ensure_one()
        if self.request_id._pending_step() != self:
            raise UserError(_(
                "Only the current pending step of the chain can be approved."))
        self.request_id.action_approve()
        return True

    def action_refuse(self):
        self.ensure_one()
        if self.request_id._pending_step() != self:
            raise UserError(_(
                "Only the current pending step of the chain can be refused."))
        self.request_id.action_refuse()
        return True
