from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PestOpsProductionSettings(models.Model):
    _name = "pestops.production.settings"
    _description = "PestOps Production Settings"
    _rec_name = "company_id"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
        index=True,
    )
    active = fields.Boolean(default=True)
    maintenance_mode = fields.Boolean(
        string="Maintenance Mode",
        help="Stops non-essential scheduled automation jobs for this company."
    )
    automation_enabled = fields.Boolean(
        string="Automations Enabled",
        default=True,
    )
    require_single_run_lock = fields.Boolean(
        string="Use Automation Run Lock",
        default=True,
    )
    stale_run_timeout_minutes = fields.Integer(
        string="Stale Run Timeout (minutes)",
        default=120,
    )
    production_label = fields.Char(
        string="Production Label",
        default="PestOps Production",
    )
    notes = fields.Text()

    _sql_constraints = [
        (
            "pestops_production_settings_company_uniq",
            "unique(company_id)",
            "Only one PestOps production settings record is allowed per company.",
        ),
    ]

    @api.model
    def get_for_company(self, company=None):
        company = company or self.env.company
        rec = self.search([("company_id", "=", company.id)], limit=1)
        if not rec:
            rec = self.create({"company_id": company.id})
        return rec


class PestOpsAutomationRun(models.Model):
    _name = "pestops.automation.run"
    _description = "PestOps Automation Run Lock"
    _order = "create_date desc"

    key = fields.Char(required=True, index=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
        index=True,
    )
    status = fields.Selection(
        [("running", "Running"), ("done", "Done"), ("failed", "Failed")],
        required=True,
        default="running",
    )
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    finished_at = fields.Datetime()
    message = fields.Text()

    _sql_constraints = [
        (
            "pestops_automation_run_key_company_uniq",
            "unique(company_id, key)",
            "An automation key may only have one active run record per company.",
        ),
    ]

    @api.model
    def acquire(self, key, company=None):
        company = company or self.env.company
        settings = self.env["pestops.production.settings"].get_for_company(company)
        if not settings.automation_enabled or settings.maintenance_mode:
            return self.env["pestops.automation.run"]

        run = self.search(
            [
                ("company_id", "=", company.id),
                ("key", "=", key),
                ("status", "=", "running"),
            ],
            limit=1,
        )
        if run:
            timeout = max(settings.stale_run_timeout_minutes, 1)
            age = fields.Datetime.now() - run.started_at
            if age.total_seconds() < timeout * 60:
                return self.env["pestops.automation.run"]
            run.write({
                "status": "failed",
                "finished_at": fields.Datetime.now(),
                "message": _("Run marked stale and released by the hardening watchdog."),
            })
        return self.create({
            "key": key,
            "company_id": company.id,
            "status": "running",
        })

    def finish(self, success=True, message=False):
        for rec in self:
            rec.write({
                "status": "done" if success else "failed",
                "finished_at": fields.Datetime.now(),
                "message": message or False,
            })


class PestOpsCronGuard(models.AbstractModel):
    _name = "pestops.cron.guard"
    _description = "PestOps Cron Guard"

    @api.model
    def run_once(self, key, callback, company=None):
        company = company or self.env.company
        lock = self.env["pestops.automation.run"].acquire(key, company=company)
        if not lock:
            return False
        try:
            callback()
            lock.finish(True)
            return True
        except Exception as exc:
            lock.finish(False, str(exc))
            raise
