# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EduflowFee(models.Model):
    _name = 'eduflow.fee'
    _description = "School Fee / Due"
    _inherit = ['mail.thread']
    _order = 'due_date'

    student_id = fields.Many2one('eduflow.student', string="Student", required=True)
    fee_type_id = fields.Many2one('eduflow.fee.type', string="Fee Type", required=True)
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year", required=True,
                               default=lambda self: self.env['eduflow.academic.year'].search(
                                   [('active_year', '=', True)], limit=1))
    installment_name = fields.Char(string="Due", help="E.g. Due 1/3")
    amount = fields.Monetary(string="Expected Amount", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    due_date = fields.Date(string="Due Date", required=True)
    payment_ids = fields.One2many('eduflow.payment', 'fee_id', string="Payments")
    paid_amount = fields.Monetary(string="Paid Amount", compute='_compute_amounts', store=True,
                                   currency_field='currency_id')
    remaining_amount = fields.Monetary(string="Remaining Amount", compute='_compute_amounts',
                                        store=True, currency_field='currency_id')
    is_overdue = fields.Boolean(string="Overdue", compute='_compute_amounts', store=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ], string="Status", compute='_compute_amounts', store=True)
    invoice_id = fields.Many2one('account.move', string="Related Invoice", copy=False,
                                  help="Odoo customer invoice generated for this fee (F1.1).")
    invoice_state = fields.Selection([
        ('not_invoiced', 'Not Invoiced'),
        ('invoiced', 'Invoiced'),
    ], string="Invoicing Status", compute='_compute_invoice_state', store=True)
    account_move_line_id = fields.Many2one('account.move.line', string="Ligne comptable", copy=False)
    company_id = fields.Many2one('res.company', string="Institution",
                                  related='student_id.company_id', store=True, readonly=True)

    # F1.3 -- automatic reminders tracking
    reminder_count = fields.Integer(string="Reminders Sent", default=0, copy=False)
    last_reminder_date = fields.Date(string="Last Reminder Date", copy=False)
    reminder_log_ids = fields.One2many('eduflow.fee.reminder.log', 'fee_id', string="Reminder Log")

    @api.depends('invoice_id', 'invoice_id.state')
    def _compute_invoice_state(self):
        for rec in self:
            rec.invoice_state = 'invoiced' if rec.invoice_id and rec.invoice_id.state != 'cancel' \
                else 'not_invoiced'

    @api.depends('payment_ids.amount', 'payment_ids.state', 'amount', 'due_date')
    def _compute_amounts(self):
        today = fields.Date.context_today(self)
        for rec in self:
            paid = sum(rec.payment_ids.filtered(lambda p: p.state == 'confirmed').mapped('amount'))
            rec.paid_amount = paid
            rec.remaining_amount = rec.amount - paid
            if rec.remaining_amount <= 0:
                rec.state = 'paid'
                rec.is_overdue = False
            elif rec.due_date and rec.due_date < today:
                rec.state = 'overdue'
                rec.is_overdue = True
            elif paid > 0:
                rec.state = 'partial'
                rec.is_overdue = False
            else:
                rec.state = 'pending'
                rec.is_overdue = False

    def action_send_reminder(self):
        """Send a reminder to the student's financial guardian(s)."""
        for rec in self:
            financial_parents = rec.student_id.parent_rel_ids.filtered(
                'is_financial').mapped('parent_id')
            parents = financial_parents or rec.student_id.parent_rel_ids.mapped('parent_id')
            body = _("A due of %(fee_type)s of amount %(amount)s %(currency)s is due on %(date)s.",
                     fee_type=rec.fee_type_id.name, amount=rec.remaining_amount,
                     currency=rec.currency_id.symbol, date=rec.due_date)
            notified = False
            for parent in parents:
                if parent.partner_id:
                    rec.message_notify(
                        partner_ids=[parent.partner_id.id],
                        body=body,
                        subject=_("Reminder - School Due"),
                    )
                    notified = True
            if notified:
                rec.reminder_count += 1
                rec.last_reminder_date = fields.Date.context_today(rec)

    # ------------------------------------------------------------------
    # F1.1 -- Customer invoice generation
    # ------------------------------------------------------------------
    def _get_invoice_partner(self):
        self.ensure_one()
        financial_rel = self.student_id.parent_rel_ids.filtered('is_financial')[:1]
        parent = financial_rel.parent_id or self.student_id.parent_rel_ids.filtered(
            'is_primary').parent_id[:1] or self.student_id.parent_rel_ids[:1].parent_id
        return parent.partner_id

    def action_create_invoice(self):
        """Generate a customer invoice (account.move) for each selected fee.
        A fee that is already invoiced (invoice_id set on a non-cancelled
        move) cannot be invoiced a second time."""
        AccountMove = self.env['account.move']
        moves = AccountMove
        for rec in self:
            if rec.invoice_id and rec.invoice_id.state != 'cancel':
                raise UserError(_("Fee '%s' has already been invoiced (%s).")
                                 % (rec.display_name, rec.invoice_id.name))
            partner = rec._get_invoice_partner()
            if not partner:
                raise UserError(_(
                    "No financial guardian with a linked contact was found for "
                    "student '%s'. Please set a financial guardian with a related "
                    "contact before generating an invoice.") % rec.student_id.display_name)
            fee_type = rec.fee_type_id
            invoice_line_vals = {
                'name': f"{fee_type.name} - {rec.student_id.display_name} - {rec.installment_name or ''}",
                'quantity': 1,
                'price_unit': rec.amount,
                'tax_ids': [(6, 0, fee_type.tax_ids.ids)],
            }
            if fee_type.account_id:
                invoice_line_vals['account_id'] = fee_type.account_id.id
            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.context_today(rec),
                'invoice_line_ids': [(0, 0, invoice_line_vals)],
                'invoice_origin': rec.display_name,
                'company_id': rec.company_id.id or self.env.company.id,
            }
            if fee_type.journal_id:
                move_vals['journal_id'] = fee_type.journal_id.id
            move = AccountMove.create(move_vals)
            rec.invoice_id = move.id
            if move.invoice_line_ids:
                rec.account_move_line_id = move.invoice_line_ids[:1].id
            moves |= move
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form' if len(moves) > 1 else 'form',
            'domain': [('id', 'in', moves.ids)],
            'res_id': moves.id if len(moves) == 1 else False,
        }

    def action_cancel_invoice(self):
        """Cancel the linked invoice and put the fee back to 'not invoiced'."""
        for rec in self:
            if rec.invoice_id and rec.invoice_id.state != 'cancel':
                rec.invoice_id.button_cancel()
            rec.invoice_id = False
            rec.account_move_line_id = False

    # ------------------------------------------------------------------
    # F1.3 -- Automatic overdue reminders (called by ir.cron)
    # ------------------------------------------------------------------
    @api.model
    def _cron_send_fee_reminders(self):
        """Daily scheduled action: sends one automatic reminder per fee and
        per configured milestone (default J-7 / J0 / J+7), tracked via
        eduflow.fee.reminder.log so the same milestone is never reminded
        twice (idempotent, safe to run more than once the same day)."""
        ICP = self.env['ir.config_parameter'].sudo()
        milestones = ICP.get_param('eduflow.reminder_milestones', '-7,0,7')
        try:
            offsets = [int(x.strip()) for x in milestones.split(',') if x.strip()]
        except ValueError:
            offsets = [-7, 0, 7]

        today = fields.Date.context_today(self)
        ReminderLog = self.env['eduflow.fee.reminder.log']
        fees = self.search([('state', 'in', ('pending', 'partial', 'overdue'))])
        for offset in offsets:
            target_date = fields.Date.add(today, days=-offset) if offset else today
            due_fees = fees.filtered(lambda f, d=target_date: f.due_date == d)
            for fee in due_fees:
                already_sent = ReminderLog.search_count([
                    ('fee_id', '=', fee.id), ('milestone', '=', offset),
                ])
                if already_sent:
                    continue
                fee.action_send_reminder()
                ReminderLog.create({
                    'fee_id': fee.id,
                    'milestone': offset,
                    'date': today,
                })
        return True
