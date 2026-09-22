from odoo import fields, models


class PestReservice(models.Model):
    _name = 'pest.reservice'
    _description = 'Pest Re-Service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.reservice'),
        readonly=True,
        copy=False,
    )
    origin_visit_id = fields.Many2one(
        'pest.visit',
        required=True,
        ondelete='restrict',
    )
    site_id = fields.Many2one(
        related='origin_visit_id.site_id',
        store=True,
        index=True,
    )
    requested_by = fields.Many2one(
        'res.partner',
        string='Requested By',
    )
    date = fields.Datetime(default=fields.Datetime.now)
    reason = fields.Selection(
        [
            ('persistent_infestation', 'Persistent Infestation'),
            ('new_infestation', 'New Infestation'),
            ('insufficient_treatment', 'Insufficient Treatment'),
            ('customer_request', 'Customer Request'),
            ('other', 'Other'),
        ],
        required=True,
        default='customer_request',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    notes = fields.Text()

    def action_open(self):
        self.write({'state': 'open'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
