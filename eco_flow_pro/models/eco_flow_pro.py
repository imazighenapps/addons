# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EcoRequest(models.Model):
    _name = "eco.request"
    _description = "Engineering Change Request"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True,
        help="Engineering change number, generated from the ECO sequence.")
    title = fields.Char(required=True, tracking=True)
    product_tmpl_id = fields.Many2one(
        "product.template", string="Product Template", required=True,
        tracking=True)
    bom_id = fields.Many2one(
        "mrp.bom", string="Bill of Materials",
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
        help="BOM updated by this change. Leave empty to use the first BOM "
             "of the product template.")
    eco_type = fields.Selection(
        [("bom", "BOM"), ("process", "Process"), ("product", "Product")],
        default="bom", required=True, tracking=True,
        help="Scope of the change: a BOM line correction, a process "
             "adjustment or a product specification update.")
    reason = fields.Text(
        help="Why this change is needed: supplier substitution, cost "
             "review, drawing revision, production feedback...")
    state = fields.Selection(
        [("draft", "Draft"), ("review", "In Review"), ("approved",
         "Approved"), ("applied", "Applied"), ("refused", "Refused")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    requested_by = fields.Many2one(
        "res.users", string="Requested By", tracking=True,
        default=lambda self: self.env.user)
    approver_id = fields.Many2one(
        "res.users", string="Approver", tracking=True, copy=False,
        help="User who approved, applied or refused the request.")
    date_effectivity = fields.Date(
        string="Effective Date", tracking=True,
        default=fields.Date.context_today,
        help="Date from which the change is considered effective on the "
             "shop floor.")
    line_ids = fields.One2many(
        "eco.line", "eco_id", string="Change Lines", copy=True)
    line_count = fields.Integer(
        string="Lines", compute="_compute_line_count")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "The engineering change number must be unique per company.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "eco.request") or "/"
        return super().create(vals_list)

    @api.depends("line_ids")
    def _compute_line_count(self):
        for eco in self:
            eco.line_count = len(eco.line_ids)

    @api.constrains("bom_id", "product_tmpl_id")
    def _check_bom_template(self):
        for eco in self:
            if eco.bom_id and eco.bom_id.product_tmpl_id \
                    != eco.product_tmpl_id:
                raise ValidationError(_(
                    "The bill of materials \"%s\" does not belong to the "
                    "product template \"%s\".",
                    eco.bom_id.display_name, eco.product_tmpl_id.name))

    def write(self, vals):
        locked = self.filtered(lambda eco: eco.state == "applied")
        if any(fname in vals for fname in (
                "product_tmpl_id", "bom_id", "line_ids")) and locked:
            raise UserError(_(
                "The engineering change \"%s\" has already been applied: "
                "its target BOM and lines can no longer be changed.",
                locked[0].name))
        return super().write(vals)

    def _get_bom(self):
        """The BOM to update: the selected one, or the first BOM of the
        product template (lowest sequence, then oldest)."""
        self.ensure_one()
        if self.bom_id:
            return self.bom_id
        return self.env["mrp.bom"].search(
            [("product_tmpl_id", "=", self.product_tmpl_id.id)],
            order="sequence, id", limit=1)

    def _check_ready(self, submitted=False):
        for eco in self:
            if submitted and not eco.line_ids:
                raise UserError(_(
                    "Add at least one change line before submitting the "
                    "engineering change \"%s\".", eco.title))

    def action_submit(self):
        for eco in self:
            if eco.state != "draft":
                raise UserError(_(
                    "Only a draft engineering change can be submitted."))
            eco._check_ready(submitted=True)
            eco.state = "review"
            eco.message_post(body=_(
                "Engineering change submitted for review by %s with %s "
                "line(s).", self.env.user.name, len(eco.line_ids)))
        return True

    def action_approve(self):
        for eco in self:
            if eco.state != "review":
                raise UserError(_(
                    "Only an engineering change under review can be "
                    "approved."))
            eco.write({
                "state": "approved",
                "approver_id": self.env.user.id,
            })
            eco.message_post(body=_(
                "Engineering change approved by %s.", self.env.user.name))
        return True

    def action_refuse(self):
        for eco in self:
            if eco.state != "review":
                raise UserError(_(
                    "Only an engineering change under review can be "
                    "refused."))
            eco.write({
                "state": "refused",
                "approver_id": self.env.user.id,
            })
            eco.message_post(body=_(
                "Engineering change refused by %s.", self.env.user.name))
        return True

    def action_apply(self):
        for eco in self:
            if eco.state != "approved":
                raise UserError(_(
                    "Only an approved engineering change can be applied to "
                    "a bill of materials."))
            bom = eco._get_bom()
            if not bom:
                raise UserError(_(
                    "No bill of materials found for the product template "
                    "\"%s\". Select a BOM on the change or create one "
                    "first.", eco.product_tmpl_id.name))
            changed = added = removed = 0
            for line in eco.line_ids:
                bom_line = bom.bom_line_ids.filtered(
                    lambda item: item.product_id == line.component_id)[:1]
                if line.change_type == "change":
                    if not bom_line:
                        raise UserError(_(
                            "Component \"%s\" is not in the BOM \"%s\": "
                            "use an Add change line, not a Change one.",
                            line.component_id.display_name,
                            bom.display_name))
                    bom_line.product_qty = line.new_qty
                    changed += 1
                elif line.change_type == "remove":
                    if not bom_line:
                        raise UserError(_(
                            "Component \"%s\" is not in the BOM \"%s\": "
                            "there is nothing to remove.",
                            line.component_id.display_name,
                            bom.display_name))
                    bom_line.unlink()
                    removed += 1
                elif line.change_type == "add":
                    if bom_line:
                        raise UserError(_(
                            "Component \"%s\" is already in the BOM "
                            "\"%s\": use a Change line to adjust its "
                            "quantity.", line.component_id.display_name,
                            bom.display_name))
                    self.env["mrp.bom.line"].create({
                        "bom_id": bom.id,
                        "product_id": line.component_id.id,
                        "product_qty": line.new_qty,
                    })
                    added += 1
            eco.write({
                "state": "applied",
                "approver_id": self.env.user.id,
            })
            eco.message_post(body=_(
                "BOM \"%s\" updated: %s quantity change(s), %s line(s) "
                "added, %s line(s) removed.", bom.display_name, changed,
                added, removed))
        return True

    def action_reset(self):
        for eco in self:
            if eco.state not in ("applied", "refused"):
                raise UserError(_(
                    "Only an applied or refused engineering change can be "
                    "reset to draft."))
            eco.state = "draft"
            eco.message_post(body=_(
                "Engineering change reset to draft by %s.",
                self.env.user.name))
        return True


class EcoLine(models.Model):
    _name = "eco.line"
    _description = "Engineering Change Line"
    _order = "eco_id, sequence, id"

    eco_id = fields.Many2one(
        "eco.request", string="Engineering Change", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    change_type = fields.Selection(
        [("add", "Add"), ("remove", "Remove"), ("change", "Change")],
        default="change", required=True,
        help="Add creates a new BOM line, Change updates the quantity of "
             "the existing line, Remove deletes it.")
    component_id = fields.Many2one(
        "product.product", string="Component", required=True)
    old_qty = fields.Float(
        string="Old Quantity", help="Quantity currently in the BOM, for "
             "reference on Change and Remove lines.")
    new_qty = fields.Float(
        string="New Quantity", help="Target quantity on the BOM after "
             "the change is applied.")
    note = fields.Text()

    _component_uniq = models.Constraint(
        "UNIQUE(eco_id, component_id)",
        "The same component can only appear once per engineering change request.")

    @api.constrains("change_type", "old_qty", "new_qty")
    def _check_quantities(self):
        for line in self:
            if line.old_qty < 0 or line.new_qty < 0:
                raise ValidationError(_(
                    "The quantities of the change line on component "
                    "\"%s\" cannot be negative.",
                    line.component_id.display_name))
            if line.change_type in ("add", "change") and line.new_qty <= 0:
                raise ValidationError(_(
                    "The new quantity of component \"%s\" must be greater "
                    "than zero on a %s line.",
                    line.component_id.display_name, line.change_type))

    def _check_parent_locked(self):
        for line in self:
            if line.eco_id.state == "applied":
                raise UserError(_(
                    "The engineering change \"%s\" has already been "
                    "applied: its lines can no longer be changed.",
                    line.eco_id.name))

    @api.model_create_multi
    def create(self, vals_list):
        seen = set()
        for vals in vals_list:
            eco_id = vals.get("eco_id")
            component_id = vals.get("component_id")
            if not (eco_id and component_id):
                continue
            if (eco_id, component_id) in seen:
                raise ValidationError(_(
                    "The component %s is already changed by this "
                    "engineering change: add one change line per "
                    "component.",
                    self.env["product.product"].browse(component_id)
                    .display_name))
            seen.add((eco_id, component_id))
            duplicate = self.search_count([
                ("eco_id", "=", eco_id),
                ("component_id", "=", component_id),
            ])
            if duplicate:
                raise ValidationError(_(
                    "The component %s is already changed by this "
                    "engineering change: add one change line per "
                    "component.",
                    self.env["product.product"].browse(component_id)
                    .display_name))
        lines = super().create(vals_list)
        lines._check_parent_locked()
        return lines

    def write(self, vals):
        self._check_parent_locked()
        return super().write(vals)
