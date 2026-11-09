# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ColdReading(models.Model):
    _name = "cold.reading"
    _description = "Cold Chain Reading"
    _inherit = ["mail.thread"]
    _order = "recorded_at desc, id desc"

    point_id = fields.Many2one(
        "cold.point", string="Cold Point", required=True, ondelete="cascade",
        index=True, tracking=True)
    temperature = fields.Float(required=True, tracking=True)
    recorded_at = fields.Datetime(
        required=True, default=fields.Datetime.now, tracking=True,
        help="When the temperature was read, not when it was typed in.")
    measured_by = fields.Many2one(
        "res.users", string="Measured By", required=True,
        default=lambda self: self.env.user)
    point_min_temp = fields.Float(
        related="point_id.min_temp", string="Point Min", readonly=True)
    point_max_temp = fields.Float(
        related="point_id.max_temp", string="Point Max", readonly=True)
    status = fields.Selection(
        [("ok", "In Range"), ("breach", "Out of Range")],
        compute="_compute_status", store=True, index=True,
        help="Set from the safe range of the cold point.")
    corrected = fields.Boolean(copy=False, tracking=True,
                               help="Ticked once the breach is explained.")
    corrected_at = fields.Datetime(readonly=True, copy=False)
    correction_note = fields.Text(
        string="Correction Note",
        help="What was done about the breach, required for the file.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("temperature", "point_id.min_temp", "point_id.max_temp")
    def _compute_status(self):
        for reading in self:
            reading.status = "breach" if (
                reading.point_id and
                (reading.temperature < reading.point_id.min_temp
                 or reading.temperature > reading.point_id.max_temp)
            ) else "ok"

    def action_correct(self):
        for reading in self:
            if reading.status != "breach":
                raise UserError(_(
                    "The reading of \"%s\" is inside the safe range, there "
                    "is nothing to correct.", reading.point_id.name))
            if not (reading.correction_note or "").strip():
                raise UserError(_(
                    "Write what was done about the breach before marking "
                    "the reading corrected."))
            reading.write({
                "corrected": True,
                "corrected_at": fields.Datetime.now(),
            })
        return True

    def action_reopen(self):
        for reading in self:
            reading.write({"corrected": False, "corrected_at": False})
        return True
