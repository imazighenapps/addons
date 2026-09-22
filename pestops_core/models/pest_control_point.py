import base64
from urllib.parse import quote

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PestControlPoint(models.Model):
    _name = 'pest.control.point'
    _description = 'Pest Control Point'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'site_id, zone_id, code'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.control.point'),
        copy=False,
        readonly=True,
    )
    site_id = fields.Many2one(
        'pest.site',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    zone_id = fields.Many2one(
        'pest.zone',
        required=True,
        ondelete='cascade',
        domain="[('site_id', '=', site_id)]",
        tracking=True,
    )
    company_id = fields.Many2one(
        related='site_id.company_id',
        store=True,
        index=True,
    )

    point_type = fields.Selection(
        [
            ('rodent_station', 'Rodent Station'),
            ('cockroach_trap', 'Cockroach Trap'),
            ('insect_light', 'Insect Light Trap'),
            ('inspection_point', 'Inspection Point'),
            ('other', 'Other'),
        ],
        default='inspection_point',
        required=True,
    )

    target_pest_ids = fields.Many2many('pest.type')
    installation_date = fields.Date()
    active = fields.Boolean(default=True)
    notes = fields.Text()

    qr_token = fields.Char(
        copy=False,
        readonly=True,
        default=lambda self: self._generate_qr_token(),
        index=True,
    )
    qr_scan_url = fields.Char(
        compute='_compute_qr_code',
        readonly=True,
    )
    qr_code_image = fields.Binary(
        compute='_compute_qr_code',
        readonly=True,
        attachment=False,
    )

    last_inspection_id = fields.Many2one(
        'pest.inspection',
        compute='_compute_history',
        store=True,
    )
    last_inspection_date = fields.Datetime(
        related='last_inspection_id.date',
        store=True,
    )
    last_activity_level = fields.Selection(
        related='last_inspection_id.activity_level',
        store=True,
    )
    next_inspection_date = fields.Datetime(
        compute='_compute_next_inspection',
        store=True,
    )

    @api.model
    def _generate_qr_token(self):
        from secrets import token_urlsafe
        return token_urlsafe(18)

    @api.depends('qr_token')
    def _compute_qr_code(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/')
        for point in self:
            if not point.qr_token:
                point.qr_scan_url = False
                point.qr_code_image = False
                continue

            relative_url = f'/pestops/scan/{quote(point.qr_token)}'
            point.qr_scan_url = f'{base_url}{relative_url}' if base_url else relative_url

            try:
                barcode = self.env['ir.actions.report'].barcode(
                    'QR',
                    point.qr_scan_url,
                    width=320,
                    height=320,
                    quiet=False,
                )
                point.qr_code_image = base64.b64encode(barcode)
            except (ValueError, AttributeError):
                point.qr_code_image = False

    @api.depends('site_id.visit_ids.inspection_ids.date', 'site_id.visit_ids.inspection_ids.line_ids.control_point_id')
    def _compute_history(self):
        for point in self:
            inspections = self.env['pest.inspection'].search(
                [('line_ids.control_point_id', '=', point.id)],
                order='date desc, id desc',
                limit=1,
            )
            point.last_inspection_id = inspections

    @api.depends('last_inspection_date')
    def _compute_next_inspection(self):
        for point in self:
            # V1 derives this from the last inspection.
            # The treatment plan frequency engine can override it in a later iteration.
            point.next_inspection_date = point.last_inspection_date

    def action_new_inspection(self):
        self.ensure_one()
        visit = self.env['pest.visit'].search([
            ('site_id', '=', self.site_id.id),
            ('technician_id', '=', self.env.user.id),
            ('state', '=', 'in_progress'),
        ], order='actual_start desc, id desc', limit=1)

        if not visit:
            visit = self.env['pest.visit'].search([
                ('site_id', '=', self.site_id.id),
                ('state', 'in', ('scheduled', 'draft')),
            ], order='scheduled_start asc, id asc', limit=1)

        if not visit:
            raise UserError(_(
                'No active PestOps visit exists for this site. '
                'Start or schedule a visit before creating an inspection.'
            ))

        inspection = self.env['pest.inspection'].create({
            'visit_id': visit.id,
            'line_ids': [(0, 0, {
                'control_point_id': self.id,
            })],
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Quick Inspection'),
            'res_model': 'pest.inspection',
            'view_mode': 'form',
            'res_id': inspection.id,
            'target': 'current',
        }
