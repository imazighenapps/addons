# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class GSheetsConnection(models.Model):
    _name = "gsheets.connection"
    _description = "Google Sheets Connection"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    spreadsheet_id = fields.Char(string="Spreadsheet ID", required=True, default="DEMO_SPREADSHEET")
    sheet_name = fields.Char(default="Sheet1")
    credential_ref = fields.Char(string="Credential Reference")
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    active = fields.Boolean(default=True)
    job_ids = fields.One2many("gsheets.job", "connection_id")

    def action_activate(self):
        for rec in self:
            if not rec.credential_ref:
                raise UserError(_("Set the credential reference before activating."))
            rec.state = "active"
        return True


class GSheetsJob(models.Model):
    _name = "gsheets.job"
    _description = "Google Sheets Export Job"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    connection_id = fields.Many2one("gsheets.connection", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    model_name = fields.Char(string="Model", required=True, help="Technical model name, e.g. sale.order")
    field_names = fields.Char(string="Fields", required=True, help="Comma-separated field names")
    domain_filter = fields.Char(string="Domain", default="[]")
    active = fields.Boolean(default=True)
    last_run_at = fields.Datetime(readonly=True)
    last_status = fields.Selection([("ok", "OK"), ("error", "Error")])
    run_ids = fields.One2many("gsheets.run", "job_id")

    @api.constrains("field_names")
    def _check_fields(self):
        for rec in self:
            if not (rec.field_names or "").strip():
                raise ValidationError(_("Provide at least one field to export."))

    def action_run(self):
        for rec in self:
            if rec.connection_id.state != "active":
                raise UserError(_("Activate the connection before running a job."))
            # Safe local run: count 0 when model unknown in this env is avoided by try.
            rows = 0
            msg = _("Export prepared.")
            status = "ok"
            try:
                if rec.model_name in self.env:
                    rows = self.env[rec.model_name].search_count([])
                else:
                    msg = _("Model not found in this database; run recorded.")
            except Exception:
                status = "error"
                msg = _("Run failed while preparing export.")
            rec.last_run_at = fields.Datetime.now()
            rec.last_status = status
            self.env["gsheets.run"].create({
                "job_id": rec.id, "status": status, "row_count": rows, "message": msg,
            })
            rec.message_post(body=_("Run completed: %s row(s).", rows))
        return True


class GSheetsRun(models.Model):
    _name = "gsheets.run"
    _description = "Google Sheets Sync Run"
    _order = "create_date desc, id desc"

    job_id = fields.Many2one("gsheets.job", required=True, ondelete="cascade")
    connection_id = fields.Many2one(related="job_id.connection_id", store=True)
    status = fields.Selection([("ok", "OK"), ("error", "Error")], required=True)
    row_count = fields.Integer()
    message = fields.Text()
