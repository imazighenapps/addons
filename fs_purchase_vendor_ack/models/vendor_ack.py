from datetime import datetime, timedelta
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError


class PurchaseVendorAck(models.Model):
    _name = 'fs.purchase.vendor.ack'
    _description = 'Purchase Order Vendor Acknowledgment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _order = 'create_date desc'

    purchase_order_id = fields.Many2one(
        'purchase.order',
        required=True,
        index=True,
        ondelete='cascade',
        check_company=True,
    )
    vendor_id = fields.Many2one(related='purchase_order_id.partner_id', store=True, index=True)
    company_id = fields.Many2one(related='purchase_order_id.company_id', store=True, index=True)
    version = fields.Integer(default=1, required=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('submitted', 'Submitted'),
            ('contested', 'Contested'),
            ('superseded', 'Superseded'),
        ],
        default='draft',
        tracking=True,
        required=True,
        index=True,
    )
    access_token = fields.Char(
        default=lambda self: uuid4().hex,
        required=True,
        copy=False,
        index=True,
    )
    expiration_date = fields.Datetime(
        default=lambda self: fields.Datetime.now() + timedelta(days=30),
        required=True,
    )
    requested_on = fields.Datetime(readonly=True)
    submitted_on = fields.Datetime(readonly=True)
    note = fields.Text()
    line_ids = fields.One2many('fs.purchase.vendor.ack.line', 'ack_id', copy=True)

    _token_unique = models.Constraint(
        'unique (access_token)',
        'Acknowledgment tokens must be unique.',
    )
    _version_unique = models.Constraint(
        'unique (purchase_order_id,version)',
        'Acknowledgment versions must be unique per purchase order.',
    )

    def _check_buyer(self):
        if not self.env.user.has_group('purchase.group_purchase_user'):
            raise AccessError(_('Only purchase users can manage supplier acknowledgments.'))

    def write(self, vals):
        workflow_context = self.env.context.get('fs_vendor_ack_transition') or self.env.context.get('fs_vendor_ack_system_change')
        protected = {'purchase_order_id', 'version', 'access_token', 'vendor_id', 'company_id', 'state'}
        if protected.intersection(vals) and not workflow_context:
            raise AccessError(_('Acknowledgment identity and workflow fields can only be changed through the workflow actions.'))
        if any(record.state == 'superseded' for record in self) and set(vals) - {'message_follower_ids'}:
            raise UserError(_('A superseded acknowledgment is historical and cannot be edited.'))
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get('fs_vendor_ack_internal'):
            raise UserError(_('Vendor acknowledgments are audit records and cannot be deleted manually.'))
        return super().unlink()

    def _is_token_valid(self):
        self.ensure_one()
        return bool(
            self.access_token
            and self.state in ('draft', 'sent')
            and (not self.expiration_date or self.expiration_date >= fields.Datetime.now())
            and self.purchase_order_id.exists()
            and self.purchase_order_id.state != 'cancel'
        )

    def get_portal_url(self):
        self.ensure_one()
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f'{base}/fs/vendor-ack/{self.id}/{self.access_token}'

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_vendor_ack_workflow'):
            raise AccessError(_('Vendor acknowledgments must be created through the purchase-order workflow.'))
        return super().create(vals_list)

    @api.model
    def create_from_purchase_order(self, purchase):
        """Create the next acknowledgment version from the current PO snapshot."""
        purchase = purchase.exists()
        if not purchase:
            raise UserError(_('The purchase order no longer exists.'))
        purchase.check_access_rights('read')
        purchase.check_access_rule('read')
        if not self.env.context.get('fs_vendor_ack_system_change'):
            self._check_buyer()

        previous_version = max(
            self.search([('purchase_order_id', '=', purchase.id)]).mapped('version') or [0]
        )
        self.search(
            [('purchase_order_id', '=', purchase.id), ('state', 'in', ('draft', 'sent'))]
        ).with_context(fs_vendor_ack_transition=True).write({'state': 'superseded'})

        lines = [
            (
                0,
                0,
                {
                    'purchase_line_id': line.id,
                    'ordered_qty': line.product_qty,
                    'ordered_uom_id': line.product_uom_id.id,
                    'confirmed_qty': line.product_qty,
                    'confirmed_date': line.date_planned,
                },
            )
            for line in purchase.order_line
            if not line.display_type and line.product_id
        ]
        return self.with_context(fs_vendor_ack_workflow=True).create({
            'purchase_order_id': purchase.id,
            'version': previous_version + 1,
            'state': 'draft',
            'line_ids': lines,
        })

    def action_send_invitation(self):
        self.ensure_one()
        self._check_buyer()
        for ack in self:
            if ack.state not in ('draft', 'submitted', 'contested'):
                raise UserError(_('Only an active acknowledgment can be sent for supplier review.'))
            if not ack.vendor_id.email:
                raise UserError(
                    _('The vendor must have an email address before an acknowledgment invitation can be sent.')
                )
            if ack.purchase_order_id.state == 'cancel':
                raise UserError(_('A cancelled purchase order cannot be sent for acknowledgment.'))
            if ack.state in ('submitted', 'contested'):
                # Start a new version instead of reopening a historical response.
                new_ack = self.create_from_purchase_order(ack.purchase_order_id)
                return new_ack.action_send_invitation()
            ack.with_context(fs_vendor_ack_transition=True).write({'state': 'sent', 'requested_on': fields.Datetime.now()})
            template = self.env.ref(
                'fs_purchase_vendor_ack.email_template_vendor_ack',
                raise_if_not_found=False,
            )
            if template:
                template.send_mail(ack.id, force_send=True)
        return True

    def action_open_portal(self):
        self.ensure_one()
        self._check_buyer()
        return {
            'type': 'ir.actions.act_url',
            'url': self.get_portal_url(),
            'target': 'new',
        }

    def submit_from_portal(self, post):
        """Apply a vendor response after validating the signed public token."""
        self.ensure_one()
        if not self._is_token_valid():
            raise AccessError(_('This acknowledgment link is expired, superseded, or no longer active.'))

        for line in self.line_ids:
            key_qty = f'qty_{line.id}'
            key_date = f'date_{line.id}'
            key_state = f'state_{line.id}'
            key_reason = f'reason_{line.id}'
            if key_qty not in post:
                continue
            try:
                qty = float(post[key_qty])
            except (TypeError, ValueError) as exc:
                raise UserError(
                    _('Invalid quantity for %(product)s.', product=line.product_id.display_name)
                ) from exc
            if qty < 0:
                raise UserError(_('Confirmed quantity cannot be negative.'))

            date_value = post.get(key_date)
            if date_value:
                try:
                    confirmed_date = datetime.strptime(date_value, '%Y-%m-%dT%H:%M')
                except ValueError as exc:
                    raise UserError(
                        _('Invalid confirmation date for %(product)s.', product=line.product_id.display_name)
                    ) from exc
            else:
                confirmed_date = line.ordered_date

            state = post.get(key_state) or ('partial' if qty < line.ordered_qty else 'confirmed')
            if state not in ('confirmed', 'partial', 'rejected'):
                state = 'confirmed'
            if state in ('partial', 'rejected') and not (post.get(key_reason) or '').strip():
                raise UserError(
                    _('A reason is required when a vendor partially confirms or rejects a line.')
                )
            # Public portal access is authorized by the unguessable acknowledgment token;
            # the token is validated above before updating these supplier-response fields.
            line.sudo().with_context(fs_vendor_ack_portal=True).write({
                'confirmed_qty': qty,
                'confirmed_date': confirmed_date,
                'state': state,
                'reason': post.get(key_reason),
            })

        state = (
            'contested'
            if any(line.state in ('partial', 'rejected') for line in self.line_ids)
            else 'submitted'
        )
        # The public portal has no backend user; token validation above is the authorization boundary.
        self.sudo().with_context(fs_vendor_ack_transition=True).write({
            'state': state,
            'submitted_on': fields.Datetime.now(),
        })
        self.sudo().message_post(body=_('Vendor acknowledgment submitted through the secure portal.'))
        if state == 'contested':
            user = self.purchase_order_id.user_id or self.purchase_order_id.create_uid
            if user:
                self.sudo().activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    summary=_('Vendor acknowledgment contains discrepancies'),
                    note=_('Review the supplier response: quantity, date, or rejection differences require buyer attention.'),
                )
        return True

    @api.model
    def _material_purchase_change(self, vals):
        return bool(
            {
                'partner_id',
                'order_line',
                'company_id',
                'currency_id',
                'payment_term_id',
            }.intersection(vals)
        )


class PurchaseVendorAckLine(models.Model):
    _name = 'fs.purchase.vendor.ack.line'
    _description = 'Purchase Vendor Acknowledgment Line'
    _check_company_auto = True

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('fs_vendor_ack_workflow'):
            raise AccessError(_('Vendor acknowledgment lines are generated from purchase orders.'))
        return super().create(vals_list)

    ack_id = fields.Many2one(
        'fs.purchase.vendor.ack',
        required=True,
        index=True,
        ondelete='cascade',
        check_company=True,
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        required=True,
        ondelete='restrict',
        check_company=True,
    )
    company_id = fields.Many2one(related='ack_id.company_id', store=True, index=True)
    product_id = fields.Many2one(related='purchase_line_id.product_id', store=True)
    ordered_qty = fields.Float(required=True, readonly=True)
    ordered_uom_id = fields.Many2one('uom.uom', required=True, readonly=True)
    ordered_date = fields.Datetime(related='purchase_line_id.date_planned', readonly=True)
    confirmed_qty = fields.Float(required=True)
    confirmed_date = fields.Datetime()
    state = fields.Selection(
        [('confirmed', 'Confirmed'), ('partial', 'Partial'), ('rejected', 'Rejected')],
        default='confirmed',
        required=True,
    )
    reason = fields.Char()
    qty_difference = fields.Float(compute='_compute_differences', store=True)
    date_difference_days = fields.Float(compute='_compute_differences', store=True)
    difference_type = fields.Selection(
        [('none', 'No Difference'), ('quantity', 'Quantity Difference'),
         ('date', 'Date Difference'), ('both', 'Quantity and Date Difference'), ('rejected', 'Rejected')],
        compute='_compute_differences', store=True,
    )

    def write(self, vals):
        protected = {
            'ack_id', 'purchase_line_id', 'ordered_qty', 'ordered_uom_id',
            'confirmed_qty', 'confirmed_date', 'state', 'reason',
        }
        if protected.intersection(vals) and not self.env.context.get('fs_vendor_ack_portal'):
            raise AccessError(
                _('Supplier response fields can only be changed through the acknowledgment workflow.')
            )
        return super().write(vals)

    @api.depends('ordered_qty', 'confirmed_qty', 'ordered_date', 'confirmed_date', 'state')
    def _compute_differences(self):
        for line in self:
            line.qty_difference = line.confirmed_qty - line.ordered_qty
            if line.ordered_date and line.confirmed_date:
                line.date_difference_days = (line.confirmed_date - line.ordered_date).total_seconds() / 86400.0
            else:
                line.date_difference_days = 0.0
            has_qty = float_compare(line.qty_difference, 0.0, precision_rounding=line.ordered_uom_id.rounding) != 0
            has_date = abs(line.date_difference_days) > 0.0001
            if line.state == 'rejected':
                line.difference_type = 'rejected'
            elif has_qty and has_date:
                line.difference_type = 'both'
            elif has_qty:
                line.difference_type = 'quantity'
            elif has_date:
                line.difference_type = 'date'
            else:
                line.difference_type = 'none'
