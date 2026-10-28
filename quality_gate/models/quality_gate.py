# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class QualityInspectionPlan(models.Model):
    _name = "quality.inspection.plan"
    _description = "Quality Control Plan"
    _inherit = ["mail.thread"]
    _order = "code, id"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        required=True, tracking=True,
        help="Short reference of the plan, for example QP-IN-01.")
    operation = fields.Selection(
        [("incoming", "Incoming"), ("outgoing", "Outgoing"),
         ("internal", "Internal Transfer"), ("workshop", "Workshop")],
        default="incoming", required=True, tracking=True,
        help="Step of the flow controlled by this plan.")
    product_id = fields.Many2one(
        "product.product", string="Product",
        help="Leave empty to apply the plan to every product.")
    product_category_id = fields.Many2one(
        "product.category", string="Product Category",
        help="Leave empty to apply the plan to every category.")
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("paused", "Paused")],
        default="draft", required=True, tracking=True, index=True)
    point_ids = fields.One2many(
        "quality.inspection.point", "plan_id", string="Control Points",
        copy=True)
    point_count = fields.Integer(compute="_compute_point_count")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "The plan code must be unique per company.")

    @api.depends("point_ids")
    def _compute_point_count(self):
        for plan in self:
            plan.point_count = len(plan.point_ids)

    def _check_limits(self):
        """A measured checkpoint needs a usable acceptance window."""
        self.ensure_one()
        for point in self.point_ids:
            if point.check_type not in ("measure", "range"):
                continue
            if point.max_value <= point.min_value:
                raise UserError(_(
                    "Set the acceptance limits on control point \"%s\": the "
                    "maximum must be greater than the minimum.",
                    point.name))

    def action_start(self):
        for plan in self:
            if plan.state != "draft":
                raise UserError(_("Only a draft plan can be started."))
            if not plan.point_ids:
                raise UserError(_(
                    "Add at least one control point before starting the plan."))
            plan._check_limits()
            plan.state = "running"
            plan.message_post(body=_(
                "Plan started with %s control point(s).",
                len(plan.point_ids)))
        return True

    def action_pause(self):
        for plan in self:
            if plan.state != "running":
                raise UserError(_("Only a running plan can be paused."))
            plan.state = "paused"
        return True

    def action_resume(self):
        for plan in self:
            if plan.state != "paused":
                raise UserError(_("Only a paused plan can be resumed."))
            plan.state = "running"
        return True

    def action_reset(self):
        for plan in self:
            if plan.state not in ("draft", "paused"):
                raise UserError(_(
                    "Pause the plan before resetting it to draft."))
            plan.state = "draft"
        return True


class QualityInspectionPoint(models.Model):
    _name = "quality.inspection.point"
    _description = "Quality Control Point"
    _order = "plan_id, sequence, id"

    plan_id = fields.Many2one(
        "quality.inspection.plan", string="Control Plan", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Checkpoint", required=True)
    check_type = fields.Selection(
        [("pass_fail", "Pass / Fail"), ("measure", "Measure"),
         ("range", "Range"), ("text", "Text")],
        default="pass_fail", required=True,
        help="Pass/fail and text are judged by the inspector. Measure and "
             "range compare the measured value with the acceptance limits.")
    instruction = fields.Text(
        help="What the inspector has to do or look at.")
    min_value = fields.Float(string="Minimum", help="Lower acceptance limit.")
    max_value = fields.Float(string="Maximum", help="Upper acceptance limit.")
    uom_id = fields.Many2one(
        "uom.uom", string="Unit of Measure",
        help="Unit of the measured value, for example mm or kg.")
    required = fields.Boolean(
        default=True, help="An inspection cannot pass without this result.")

    @api.constrains("check_type", "min_value", "max_value")
    def _check_range(self):
        for point in self:
            if point.check_type != "range":
                continue
            # A new line in the editable list has no limits yet: only check
            # once at least one bound has been entered.
            if not point.min_value and not point.max_value:
                continue
            if point.max_value <= point.min_value:
                raise ValidationError(_(
                    "On control point \"%s\", the maximum value must be "
                    "greater than the minimum value.", point.name))


class QualityInspection(models.Model):
    _name = "quality.inspection"
    _description = "Quality Inspection"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True)
    plan_id = fields.Many2one(
        "quality.inspection.plan", string="Control Plan", required=True,
        tracking=True, domain=[("state", "=", "running")])
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, tracking=True)
    lot_id = fields.Many2one("stock.lot", string="Lot / Serial Number")
    picking_id = fields.Many2one("stock.picking", string="Transfer")
    partner_id = fields.Many2one("res.partner", string="Partner")
    quantity = fields.Float(default=1.0, help="Inspected quantity.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"),
         ("passed", "Passed"), ("failed", "Failed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    result_ids = fields.One2many(
        "quality.inspection.result", "inspection_id", string="Checkpoints",
        copy=True)
    issue_ids = fields.One2many(
        "quality.issue", "inspection_id", string="Non-Conformities")
    result_count = fields.Integer(compute="_compute_result_counts")
    failed_count = fields.Integer(
        string="Not Passed", compute="_compute_result_counts")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "quality.inspection") or "/"
        return super().create(vals_list)

    @api.depends("result_ids", "result_ids.passed")
    def _compute_result_counts(self):
        for inspection in self:
            inspection.result_count = len(inspection.result_ids)
            inspection.failed_count = len(
                inspection.result_ids.filtered(lambda result: not result.passed))

    def write(self, vals):
        if "plan_id" in vals:
            for inspection in self:
                if inspection.state != "draft":
                    raise UserError(_(
                        "The control plan cannot be changed once the "
                        "inspection has started."))
        return super().write(vals)

    def action_start(self):
        for inspection in self:
            if inspection.state != "draft":
                raise UserError(_("Only a draft inspection can be started."))
            if inspection.plan_id.state != "running":
                raise UserError(_(
                    "Start the control plan \"%s\" before inspecting.",
                    inspection.plan_id.name))
            points = inspection.plan_id.point_ids
            if not points:
                raise UserError(_(
                    "The control plan \"%s\" has no control point.",
                    inspection.plan_id.name))
            existing = inspection.result_ids.mapped("point_id")
            vals_list = [{
                "inspection_id": inspection.id,
                "point_id": point.id,
            } for point in points if point not in existing]
            if vals_list:
                self.env["quality.inspection.result"].create(vals_list)
            inspection.state = "in_progress"
            inspection.message_post(body=_(
                "%(count)s checkpoint(s) loaded from plan %(plan)s.",
                count=len(points), plan=inspection.plan_id.name))
        return True

    def _check_measurements(self):
        """Validate measure/range results and store their verdict.

        Returns the names of the checkpoints whose measured value is outside
        the acceptance limits. Nothing is written when a value is out of
        tolerance, so the inspector can still correct it or fail the
        inspection.
        """
        self.ensure_one()
        out_of_limits = []
        for result in self.result_ids:
            point = result.point_id
            if point.check_type not in ("measure", "range"):
                continue
            if not (point.min_value <= result.value_float <= point.max_value):
                out_of_limits.append(point.name)
            else:
                result.passed = True
        return out_of_limits

    def action_pass(self):
        for inspection in self:
            if inspection.state != "in_progress":
                raise UserError(_(
                    "Only an inspection in progress can be passed."))
            out_of_limits = inspection._check_measurements()
            if out_of_limits:
                raise UserError(_(
                    "Measured values are outside the acceptance limits for: "
                    "%s. Correct the values or fail the inspection.",
                    ", ".join(out_of_limits)))
            missing = []
            failed = []
            for point in inspection.plan_id.point_ids:
                if not point.required:
                    continue
                result = inspection.result_ids.filtered(
                    lambda item, checkpoint=point:
                    item.point_id == checkpoint)[:1]
                if not result:
                    missing.append(point.name)
                elif not result.passed:
                    failed.append(point.name)
            if missing:
                raise UserError(_(
                    "No result recorded for the required checkpoint(s): %s.",
                    ", ".join(missing)))
            if failed:
                raise UserError(_(
                    "The required checkpoint(s) did not pass: %s. Use the "
                    "Fail button to record a non-conformity.",
                    ", ".join(failed)))
            inspection.state = "passed"
            inspection.message_post(body=_(
                "Inspection passed by %s.", self.env.user.name))
        return True

    def action_fail(self):
        for inspection in self:
            if inspection.state not in ("draft", "in_progress"):
                raise UserError(_("Only an open inspection can be failed."))
            failed = inspection.result_ids.filtered(
                lambda result: not result.passed)
            if not failed and not inspection.note:
                raise UserError(_(
                    "Record at least one failed checkpoint or explain the "
                    "failure in the notes before failing this inspection."))
            inspection.state = "failed"
            inspection.message_post(body=_(
                "Inspection failed: %s checkpoint(s) not passed.",
                len(failed)))
        return True

    def action_cancel(self):
        for inspection in self:
            if inspection.state == "cancelled":
                raise UserError(_("This inspection is already cancelled."))
            inspection.state = "cancelled"
        return True

    def action_reset(self):
        for inspection in self:
            if inspection.state == "draft":
                continue
            inspection.state = "draft"
            inspection.message_post(body=_(
                "Inspection reset to draft by %s.", self.env.user.name))
        return True


class QualityInspectionResult(models.Model):
    _name = "quality.inspection.result"
    _description = "Quality Inspection Result"
    _order = "inspection_id, id"

    inspection_id = fields.Many2one(
        "quality.inspection", string="Inspection", required=True,
        ondelete="cascade", index=True)
    point_id = fields.Many2one(
        "quality.inspection.point", string="Checkpoint", required=True)
    check_type = fields.Selection(
        related="point_id.check_type", store=True, readonly=True)
    value_float = fields.Float(string="Measured Value")
    value_text = fields.Char(string="Observation")
    passed = fields.Boolean(
        string="Passed",
        help="For pass/fail and text checkpoints the inspector decides. For "
             "measure and range checkpoints the verdict is computed from the "
             "measured value and the acceptance limits.")
    note = fields.Text()

    _point_uniq = models.Constraint(
        "UNIQUE(inspection_id, point_id)",
        "A checkpoint can only be evaluated once per inspection.")

    # The `passed` flag is deliberately a plain Boolean: it must stay
    # editable for pass/fail and text checkpoints. For measure and range
    # checkpoints it is prefilled by the onchange below (UI) and recomputed
    # by QualityInspection._check_measurements() before an inspection can
    # pass. A result is created empty when the inspection starts, so a hard
    # "value is required" constraint would block the workflow; instead the
    # constraint below refuses an inconsistent stored state (a measured
    # checkpoint marked as passed while its value is outside the limits).
    @api.onchange("point_id", "value_float")
    def _onchange_value_float(self):
        for result in self:
            point = result.point_id
            if point and point.check_type in ("measure", "range"):
                result.passed = (
                    point.min_value <= result.value_float <= point.max_value)

    @api.constrains("passed", "value_float", "point_id")
    def _check_measured_value(self):
        for result in self:
            point = result.point_id
            if not point or point.check_type not in ("measure", "range"):
                continue
            if result.passed and not (
                    point.min_value <= result.value_float <= point.max_value):
                raise ValidationError(_(
                    "Checkpoint \"%s\" cannot pass: the measured value must "
                    "be between %s and %s.",
                    point.name, point.min_value, point.max_value))

    @api.constrains("point_id", "inspection_id")
    def _check_point_plan(self):
        for result in self:
            if result.point_id.plan_id != result.inspection_id.plan_id:
                raise ValidationError(_(
                    "The checkpoint \"%s\" does not belong to the control "
                    "plan of this inspection.", result.point_id.name))


class QualityIssue(models.Model):
    _name = "quality.issue"
    _description = "Quality Non-Conformity"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True)
    inspection_id = fields.Many2one(
        "quality.inspection", string="Inspection",
        ondelete="set null", index=True)
    product_id = fields.Many2one("product.product", string="Product")
    partner_id = fields.Many2one("res.partner", string="Partner")
    description = fields.Text(required=True)
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        default="minor", required=True, tracking=True)
    root_cause = fields.Text()
    corrective_action = fields.Text()
    owner_id = fields.Many2one(
        "res.users", string="Owner", tracking=True,
        default=lambda self: self.env.user)
    state = fields.Selection(
        [("open", "Open"), ("analysis", "In Analysis"),
         ("closed", "Closed")],
        default="open", required=True, tracking=True, index=True)
    closed_date = fields.Date(readonly=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "quality.issue") or "/"
        return super().create(vals_list)

    def action_analyse(self):
        for issue in self:
            if issue.state != "open":
                raise UserError(_(
                    "Only an open non-conformity can be analysed."))
            issue.state = "analysis"
        return True

    def action_close(self):
        for issue in self:
            if issue.state == "closed":
                raise UserError(_("This non-conformity is already closed."))
            if issue.severity in ("major", "critical") \
                    and not issue.corrective_action:
                raise UserError(_(
                    "Describe the corrective action before closing a major "
                    "or critical non-conformity."))
            issue.write({
                "state": "closed",
                "closed_date": fields.Date.context_today(issue),
            })
            issue.message_post(body=_(
                "Non-conformity closed by %s.", self.env.user.name))
        return True

    def action_reopen(self):
        for issue in self:
            if issue.state != "closed":
                raise UserError(_(
                    "Only a closed non-conformity can be reopened."))
            issue.write({"state": "open", "closed_date": False})
        return True
