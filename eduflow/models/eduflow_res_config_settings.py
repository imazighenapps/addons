# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """F4.2 -- centralizes EduFlow global parameters in Settings > General
    instead of leaving them hard-coded. Values are stored as
    ir.config_parameter; defaults reproduce the module's previous
    behaviour (backward compatible)."""
    _inherit = 'res.config.settings'

    eduflow_account_sync_enabled = fields.Boolean(
        string="Sync confirmed payments to Accounting",
        config_parameter='eduflow.account_sync_enabled',
        help="When enabled (default), confirming an eduflow.payment on an "
             "invoiced fee creates/reconciles a matching account.payment (F1.2).")
    eduflow_require_complete_documents = fields.Boolean(
        string="Block acceptance until admission documents are complete",
        config_parameter='eduflow.require_complete_documents',
        help="When enabled, an admission cannot move to 'Accepted' while "
             "required documents are still missing (F3.3).")
    eduflow_reminder_milestones = fields.Char(
        string="Fee reminder milestones (days, comma-separated)",
        config_parameter='eduflow.reminder_milestones',
        default='-7,0,7',
        help="Days relative to the due date at which an automatic reminder "
             "is sent (negative = before, 0 = due date, positive = after). "
             "Example: -7,0,7 (F1.3).")
    eduflow_absenteeism_alert_threshold = fields.Float(
        string="Absenteeism alert threshold (%)",
        config_parameter='eduflow.absenteeism_alert_threshold',
        default=20.0,
        help="Absenteeism rate (%) above which the management dashboard "
             "highlights a class/student as at-risk.")
    eduflow_report_card_legal_mention = fields.Text(
        string="Report card legal mention",
        config_parameter='eduflow.report_card_legal_mention',
        help="Free text printed at the bottom of the PDF report card "
             "(e.g. accreditation number, official mentions).")
