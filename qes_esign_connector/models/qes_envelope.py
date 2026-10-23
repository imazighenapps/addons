# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class QesEnvelope(models.Model):
    _name = "qes.envelope"
    _description = "QES Signature Envelope"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    name = fields.Char(required=True, tracking=True)
    account_id = fields.Many2one("qes.account", string="Account", required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    res_model = fields.Char(string="Source Model")
    res_id = fields.Integer(string="Source ID")
    state = fields.Selection(
        [
            ("draft", "Draft"), ("ready", "Ready"), ("sent", "Sent"),
            ("partial", "Partially Signed"), ("signed", "Signed"),
            ("completed", "Completed"), ("archived", "Archived"),
            ("expired", "Expired"), ("refused", "Refused"), ("error", "Error"),
        ],
        default="draft",
        tracking=True,
    )
    provider_tx_id = fields.Char(string="Provider Transaction ID", copy=False)
    expiry_date = fields.Date()
    participant_ids = fields.One2many("qes.participant", "envelope_id")
    document_ids = fields.One2many("qes.document", "envelope_id")
    event_ids = fields.One2many("qes.event", "envelope_id")
    signed_pdf_id = fields.Many2one("ir.attachment", string="Signed PDF", copy=False)
    validation_report = fields.Text(string="Validation Report", copy=False)

    def _log(self, etype, details="", actor="", ip=""):
        prev = self.event_ids[:1].event_hash if self.event_ids else "GENESIS"
        payload = "%s|%s|%s|%s|%s" % (self.id, etype, actor, details, prev)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.env["qes.event"].sudo().create({
            "envelope_id": self.id, "etype": etype, "actor": actor, "ip": ip,
            "details": details, "prev_hash": prev, "event_hash": digest,
        })

    def action_prepare(self):
        for env in self:
            if not env.document_ids or not env.participant_ids:
                raise UserError(_("Add at least one document and one participant first."))
            env.state = "ready"
            env._log("prepared", "Envelope prepared with %d document(s), %d participant(s)."
                     % (len(env.document_ids), len(env.participant_ids)))

    def action_prepare(self):
        for env in self:
            if not env.document_ids or not env.participant_ids:
                raise UserError(_("Add at least one document and one participant first."))
            env.state = "ready"
            env._log("prepared", "Envelope prepared: %d document(s), %d participant(s)."
                     % (len(env.document_ids), len(env.participant_ids)))

    def action_start(self):
        for env in self:
            code = env.account_id.provider_id.code
            if code == "demo":
                env._demo_start()
            elif code == "universign":
                env._universign_start()
            else:
                raise UserError(_("This provider is a stub in this version."))

    def _demo_start(self):
        self.ensure_one()
        self.provider_tx_id = "DEMO-%06d" % self.id
        self.state = "sent"
        for part in self.participant_ids:
            part.sign_url = "demo://sign/%s/%s" % (self.provider_tx_id, part.access_token or part.id)
        self._log("sent", "Demo transaction %s started." % self.provider_tx_id)

    def _universign_start(self):
        self.ensure_one()
        account = self.account_id
        if not account.api_key:
            raise UserError(_("Universign API key is missing on the account."))
        import requests
        base = (account.provider_id.api_base or "https://api.universign.com/v1").rstrip("/")
        headers = {"Authorization": "Basic %s" % account.api_key,
                   "Content-Type": "application/json"}
        try:
            resp = requests.post(base + "/transactions", json={"name": self.name}, headers=headers, timeout=25)
            data = resp.json()
            self.provider_tx_id = data.get("id")
            self.state = "sent"
            self._log("sent", "Universign transaction %s created." % self.provider_tx_id)
        except Exception as exc:
            _logger.warning("Universign start failed: %s", exc)
            self.state = "error"
            self._log("error", str(exc))
            raise UserError(_("Universign submission failed: %s") % exc)

    def action_check_status(self):
        for env in self:
            if env.account_id.provider_id.code == "universign" and env.provider_tx_id:
                env._universign_status()
            else:
                env._log("status", "Status checked (demo provider: see participants).")

    def _universign_status(self):
        self.ensure_one()
        import requests
        account = self.account_id
        base = (account.provider_id.api_base or "https://api.universign.com/v1").rstrip("/")
        headers = {"Authorization": "Basic %s" % account.api_key}
        try:
            resp = requests.get(base + "/transactions/%s" % self.provider_tx_id, headers=headers, timeout=25)
            state = resp.json().get("state")
            mapping = {"closed": "signed", "expired": "expired", "cancelled": "refused"}
            self.state = mapping.get(state, self.state)
            self._log("status", "Provider state: %s." % state)
        except Exception as exc:
            self._log("error", str(exc))

    def action_fetch_evidence(self):
        for env in self:
            evidence = {
                "envelope": env.name,
                "provider_tx": env.provider_tx_id,
                "state": env.state,
                "participants": [
                    {"email": p.email, "required": p.required_level,
                     "obtained": p.obtained_level, "signed_on": str(p.signed_on or ""),
                     "cert": p.cert_info or ""} for p in env.participant_ids],
                "events": [
                    {"ts": str(e.create_date), "type": e.etype, "actor": e.actor,
                     "hash": e.event_hash, "prev": e.prev_hash} for e in env.event_ids],
            }
            blob = json.dumps(evidence, indent=2).encode("utf-8")
            env.validation_report = blob.decode("utf-8")
            self.env["ir.attachment"].create({
                "name": "%s_evidence.json" % env.name.replace(" ", "_"),
                "raw": base64.b64encode(blob),
                "res_model": env._name,
                "res_id": env.id,
                "mimetype": "application/json",
            })
            env._log("evidence", "Evidence file generated.")

    def _demo_finalize(self):
        self.ensure_one()
        src = self.document_ids[:1].attachment_id
        if src:
            self.signed_pdf_id = src.copy({
                "name": "signed_%s" % (src.name or "document.pdf"),
                "res_model": self._name,
                "res_id": self.id,
            }).id
        self._log("finalized", "All signers completed; signed document ready.")

    def action_archive(self):
        self.write({"state": "archived"})
        for env in self:
            env._log("archived", "Envelope archived.")

    @api.model
    def _cron_poll_status(self):
        for env in self.search([("state", "in", ("sent", "partial"))]):
            try:
                env.action_check_status()
            except Exception as exc:
                _logger.warning("QES poll failed for %s: %s", env.name, exc)
        return True
