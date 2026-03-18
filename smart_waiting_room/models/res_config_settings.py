# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ── Queue Behaviour ───────────────────────────────────────────────────────

    waiting_room_audio_enabled = fields.Boolean(
        string='Audio Announcements',
        config_parameter='smart_waiting_room.audio_enabled',
        default=True,
    )

    waiting_room_show_estimated_time = fields.Boolean(
        string='Show Estimated Wait Time on Display',
        config_parameter='smart_waiting_room.show_estimated_time',
        default=True,
    )

    waiting_room_auto_no_show_minutes = fields.Integer(
        string='Auto No-Show After (minutes)',
        config_parameter='smart_waiting_room.auto_no_show_minutes',
        default=10,
    )

    waiting_room_late_threshold = fields.Integer(
        string='Overdue Threshold (minutes)',
        config_parameter='smart_waiting_room.late_threshold',
        default=45,
    )
