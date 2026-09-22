from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import hashlib


class PestInterventionProof(models.Model):
    _name = "pest.intervention.proof"
    _description = "PestOps Intervention Proof"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "visit_id desc, id desc"

    name = fields.Char(
        string="Proof Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    visit_id = fields.Many2one("pest.visit", required=True, ondelete="cascade", index=True, tracking=True)
    site_id = fields.Many2one(related="visit_id.site_id", store=True, readonly=True)
    partner_id = fields.Many2one("res.partner", related="site_id.partner_id", store=True, readonly=True)
    technician_id = fields.Many2one("res.users", related="visit_id.technician_id", store=True, readonly=True)

    state = fields.Selection([
        ("draft", "Draft"),
        ("prepared", "Prepared"),
        ("accepted", "Customer Accepted"),
        ("signed", "Signed"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True, copy=False)

    customer_name = fields.Char(string="Customer Signatory")
    customer_role = fields.Char(string="Customer Role")
    customer_comment = fields.Text(string="Customer Comment")
    customer_signature = fields.Binary(string="Customer Signature", attachment=True, copy=False)
    customer_accepted_at = fields.Datetime(string="Customer Accepted At", readonly=True, copy=False)
    technician_signature = fields.Binary(string="Technician Signature", attachment=True, copy=False)
    signed_at = fields.Datetime(string="Signed At", readonly=True, copy=False)

    evidence_ids = fields.One2many("pest.intervention.evidence", "proof_id", string="Evidence")
    evidence_count = fields.Integer(compute="_compute_evidence_count", store=True)
    equipment_ids = fields.Many2many(
        "pest.equipment",
        "pest_proof_equipment_rel", "proof_id", "equipment_id",
        string="Equipment Used",
    )
    treatment_ids = fields.Many2many(
        "pest.treatment",
        "pest_proof_treatment_rel", "proof_id", "treatment_id",
        string="Treatments",
    )
    inspection_ids = fields.Many2many(
        "pest.inspection",
        "pest_proof_inspection_rel", "proof_id", "inspection_id",
        string="Inspections",
    )

    proof_hash = fields.Char(string="Proof Hash", readonly=True, copy=False)
    is_signed = fields.Boolean(compute="_compute_is_signed", store=True)
    signature_ready = fields.Boolean(
        compute="_compute_signature_ready",
        string="Ready to Sign",
    )

    @api.depends("evidence_ids")
    def _compute_evidence_count(self):
        for rec in self:
            rec.evidence_count = len(rec.evidence_ids)

    @api.depends("state", "customer_signature", "technician_signature")
    def _compute_is_signed(self):
        for rec in self:
            rec.is_signed = bool(
                rec.state == "signed"
                and rec.customer_signature
                and rec.technician_signature
            )

    @api.depends("customer_name", "customer_signature", "technician_signature")
    def _compute_signature_ready(self):
        for rec in self:
            rec.signature_ready = bool(
                rec.customer_name and rec.customer_signature and rec.technician_signature
            )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = sequence.next_by_code("pest.intervention.proof") or _("New")
        return super().create(vals_list)

    def _hash_payload(self):
        self.ensure_one()
        evidence_fingerprints = []
        for evidence in self.evidence_ids.sorted("sequence"):
            evidence_fingerprints.append(
                "|".join([
                    str(evidence.sequence),
                    evidence.category or "",
                    evidence.title or "",
                    str(evidence.captured_at or ""),
                    str(evidence.sha256 or ""),
                ])
            )
        payload = "|".join([
            str(self.id),
            str(self.visit_id.id),
            str(self.partner_id.id or 0),
            self.customer_name or "",
            str(self.customer_accepted_at or ""),
            str(self.signed_at or ""),
            *evidence_fingerprints,
        ])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def action_prepare(self):
        self.write({"state": "prepared"})
        self.message_post(body=_("Intervention proof prepared."))

    def action_customer_accept(self):
        for rec in self:
            if rec.state not in ("draft", "prepared"):
                raise UserError(_("Only draft or prepared proofs can be accepted."))
            if not rec.customer_name:
                raise ValidationError(_("Please enter the customer signatory name."))
            if not rec.customer_signature:
                raise ValidationError(_("Please capture the customer signature."))
            now = fields.Datetime.now()
            rec.write({
                "state": "accepted",
                "customer_accepted_at": now,
            })
            rec.message_post(body=_("Customer acceptance recorded for %s.") % rec.customer_name)

    def action_sign(self):
        for rec in self:
            if rec.state != "accepted":
                raise UserError(_("Customer acceptance is required before signing."))
            if not rec.technician_signature:
                raise ValidationError(_("Please capture the technician signature."))
            now = fields.Datetime.now()
            rec.write({
                "state": "signed",
                "signed_at": now,
                "proof_hash": rec._hash_payload(),
            })
            if rec.visit_id:
                rec.visit_id.write({
                    "customer_signature": rec.customer_signature,
                    "customer_signature_name": rec.customer_name,
                    "customer_signature_date": rec.customer_accepted_at,
                    "customer_signature_note": rec.customer_comment,
                })
            rec.message_post(body=_("Intervention proof signed and sealed."))

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset(self):
        self.write({
            "state": "draft",
            "customer_accepted_at": False,
            "signed_at": False,
            "proof_hash": False,
        })

    def action_print(self):
        self.ensure_one()
        return self.env.ref("pestops_proof.action_pest_intervention_proof_report").report_action(self)


class PestVisit(models.Model):
    _inherit = "pest.visit"

    proof_id = fields.Many2one("pest.intervention.proof", string="Intervention Proof", copy=False)
    proof_state = fields.Selection(related="proof_id.state", string="Proof State", readonly=True)
    proof_required = fields.Boolean(
        string="Proof Required",
        default=False,
        help="Require a signed intervention proof before closing the visit.",
    )

    def action_create_intervention_proof(self):
        self.ensure_one()
        if not self.proof_id:
            equipment_ids = self.equipment_usage_ids.mapped("equipment_id").ids if "equipment_usage_ids" in self._fields else []
            self.proof_id = self.env["pest.intervention.proof"].create({
                "visit_id": self.id,
                "equipment_ids": [(6, 0, equipment_ids)],
                "treatment_ids": [(6, 0, self.treatment_ids.ids)],
                "inspection_ids": [(6, 0, self.inspection_ids.ids)],
            })
        return {
            "type": "ir.actions.act_window",
            "name": _("Intervention Proof"),
            "res_model": "pest.intervention.proof",
            "view_mode": "form",
            "res_id": self.proof_id.id,
            "target": "current",
        }

    def action_done(self):
        for visit in self:
            if visit.proof_required and visit.proof_id and visit.proof_id.state != "signed":
                raise UserError(_("A signed intervention proof is required before completing this visit."))
            if visit.proof_required and not visit.proof_id:
                raise UserError(_("Create the intervention proof before completing this visit."))
        result = super().action_done()
        for visit in self:
            if visit.proof_id and visit.proof_id.state != "cancelled":
                visit.message_post(body=_("Intervention proof state: %s.") % (visit.proof_id.state,))
        return result
