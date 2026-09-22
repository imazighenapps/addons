from odoo import api, fields, models, _


class PestOpsAutomationGuard(models.Model):
    _name = "pestops.automation.guard"
    _description = "PestOps Automation Guard"

    @api.model
    def clean_stale_runs(self):
        stale = self.env["pestops.automation.run"].search(
            [("status", "=", "running")]
        )
        changed = 0
        for run in stale:
            settings = self.env["pestops.production.settings"].get_for_company(run.company_id)
            timeout = max(settings.stale_run_timeout_minutes, 1)
            age = fields.Datetime.now() - run.started_at
            if age.total_seconds() >= timeout * 60:
                run.write({
                    "status": "failed",
                    "finished_at": fields.Datetime.now(),
                    "message": _("Released by the stale-run watchdog."),
                })
                changed += 1
        return changed
