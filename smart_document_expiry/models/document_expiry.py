# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class DocumentExpiry(models.Model):
    _name = 'document.expiry'
    _description = 'Document Expiry Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date asc, name'

    # ── Core fields ──────────────────────────────────────────────────────────
    name = fields.Char(
        string='Document Name',
        required=True,
        tracking=True,
    )
    reference = fields.Char(
        string='Reference / Number',
        tracking=True,
        help='Official document number, permit ID, policy number, etc.',
    )
    document_type_id = fields.Many2one(
        comodel_name='document.expiry.type',
        string='Document Type',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    entity_type = fields.Selection(
        selection=[
            ('person',    'Person / Employee'),
            ('vendor',    'Vendor / Partner'),
            ('vehicle',   'Vehicle'),
            ('equipment', 'Equipment'),
            ('other',     'Other'),
        ],
        string='Entity Type',
        required=True,
        tracking=True,
    )

    # ── Entity relations (one active at a time) ───────────────────────────
    person_id = fields.Many2one(
        comodel_name='document.person',
        string='Person',
        tracking=True,
        domain="[('active','=',True)]",
    )
    partner_id = fields.Many2one(
        comodel_name='document.partner',
        string='Vendor / Partner',
        tracking=True,
        domain="[('active','=',True)]",
    )
    vehicle_id = fields.Many2one(
        comodel_name='document.vehicle',
        string='Vehicle',
        tracking=True,
        domain="[('active','=',True)]",
    )
    equipment_id = fields.Many2one(
        comodel_name='document.equipment',
        string='Equipment',
        tracking=True,
        domain="[('active','=',True)]",
    )
    # For entity_type == 'other': free-text description
    other_entity_name = fields.Char(
        string='Entity Description',
        help='Describe the entity when type is "Other".',
        tracking=True,
    )

    # ── Dates ──────────────────────────────────────────────────────────────
    issue_date = fields.Date(string='Issue Date', tracking=True)
    expiry_date = fields.Date(
        string='Expiry Date',
        required=True,
        tracking=True,
        index=True,
    )

    # ── Responsible people ─────────────────────────────────────────────────
    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )
    notify_ids = fields.Many2many(
        comodel_name='res.users',
        relation='document_expiry_notify_rel',
        column1='document_id',
        column2='user_id',
        string='Also Notify',
    )

    # ── Status ────────────────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('valid',          'Valid'),
            ('expiring_soon',  'Expiring Soon'),
            ('expired',        'Expired'),
            ('renewed',        'Renewed'),
            ('archived',       'Archived'),
        ],
        string='Status',
        compute='_compute_state',
        store=True,
        tracking=True,
        index=True,
    )
    days_until_expiry = fields.Integer(
        string='Days Until Expiry',
        compute='_compute_days_until_expiry',
        store=True,
    )

    # ── Alert tracking ────────────────────────────────────────────────────
    alert_90_sent    = fields.Boolean(default=False, copy=False)
    alert_30_sent    = fields.Boolean(default=False, copy=False)
    alert_7_sent     = fields.Boolean(default=False, copy=False)
    escalation_sent  = fields.Boolean(default=False, copy=False)

    # ── Attachments ───────────────────────────────────────────────────────
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='document_expiry_attachment_rel',
        column1='document_id',
        column2='attachment_id',
        string='Attachments',
    )
    attachment_count = fields.Integer(
        string='Attachments',
        compute='_compute_attachment_count',
    )

    # ── Renewal history ───────────────────────────────────────────────────
    previous_document_id = fields.Many2one(
        comodel_name='document.expiry',
        string='Renewed From',
        ondelete='set null',
        copy=False,
    )
    renewal_count = fields.Integer(
        string='Times Renewed',
        compute='_compute_renewal_count',
    )

    # ── Notes & company ───────────────────────────────────────────────────
    notes = fields.Html(string='Notes', sanitize=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    color = fields.Integer(string='Kanban Color', compute='_compute_color', store=True)

    # ─────────────────────────────────────────────────────────────────────
    # Computes
    # ─────────────────────────────────────────────────────────────────────

    @api.depends('expiry_date')
    def _compute_days_until_expiry(self):
        today = date.today()
        for rec in self:
            rec.days_until_expiry = (rec.expiry_date - today).days if rec.expiry_date else 0

    @api.depends('expiry_date')
    def _compute_state(self):
        today = date.today()
        for rec in self:
            if rec.state in ('renewed', 'archived'):
                continue
            if not rec.expiry_date:
                rec.state = 'valid'
                continue
            days = (rec.expiry_date - today).days
            if days < 0:
                rec.state = 'expired'
            elif days <= 30:
                rec.state = 'expiring_soon'
            else:
                rec.state = 'valid'

    @api.depends('state')
    def _compute_color(self):
        color_map = {
            'valid': 10, 'expiring_soon': 3, 'expired': 9,
            'renewed': 0, 'archived': 0,
        }
        for rec in self:
            rec.color = color_map.get(rec.state, 0)

    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    def _compute_renewal_count(self):
        for rec in self:
            count, doc = 0, rec
            while doc.previous_document_id:
                count += 1
                doc = doc.previous_document_id
            rec.renewal_count = count

    # ── Display name ──────────────────────────────────────────────────────
    def _compute_display_name(self):
        for rec in self:
            entity = (
                rec.person_id.name or rec.partner_id.name
                or rec.vehicle_id.name or rec.equipment_id.name
                or rec.other_entity_name or ''
            )
            rec.display_name = f'{rec.name} [{entity}]' if entity else rec.name

    # ─────────────────────────────────────────────────────────────────────
    # Onchanges
    # ─────────────────────────────────────────────────────────────────────

    @api.onchange('entity_type')
    def _onchange_entity_type(self):
        self.person_id    = False
        self.partner_id   = False
        self.vehicle_id   = False
        self.equipment_id = False
        self.other_entity_name = False

    @api.onchange('document_type_id')
    def _onchange_document_type(self):
        if self.document_type_id and self.document_type_id.entity_type != 'all':
            self.entity_type = self.document_type_id.entity_type

    # ─────────────────────────────────────────────────────────────────────
    # Constraints
    # ─────────────────────────────────────────────────────────────────────

    @api.constrains('entity_type', 'person_id', 'partner_id', 'vehicle_id',
                    'equipment_id', 'other_entity_name')
    def _check_entity(self):
        for rec in self:
            if rec.entity_type == 'person'    and not rec.person_id:
                raise UserError(_('Please select a Person.'))
            if rec.entity_type == 'vendor'    and not rec.partner_id:
                raise UserError(_('Please select a Vendor / Partner.'))
            if rec.entity_type == 'vehicle'   and not rec.vehicle_id:
                raise UserError(_('Please select a Vehicle.'))
            if rec.entity_type == 'equipment' and not rec.equipment_id:
                raise UserError(_('Please select an Equipment.'))
            if rec.entity_type == 'other'     and not rec.other_entity_name:
                raise UserError(_('Please describe the entity.'))

    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for rec in self:
            if rec.issue_date and rec.expiry_date and rec.issue_date >= rec.expiry_date:
                raise UserError(_('Issue Date must be earlier than Expiry Date.'))

    # ─────────────────────────────────────────────────────────────────────
    # Alerts (cron)
    # ─────────────────────────────────────────────────────────────────────

    def _get_alert_threshold(self, threshold_name):
        defaults = {'alert_days_1': 90, 'alert_days_2': 30, 'alert_days_3': 7}
        if self.document_type_id:
            return getattr(self.document_type_id, threshold_name, defaults[threshold_name])
        return defaults[threshold_name]

    @api.model
    def _cron_send_expiry_alerts(self):
        today = date.today()
        docs = self.search([('state', 'not in', ['renewed', 'archived'])])
        for doc in docs:
            if not doc.expiry_date:
                continue
            days = (doc.expiry_date - today).days
            d1 = doc._get_alert_threshold('alert_days_1')
            d2 = doc._get_alert_threshold('alert_days_2')
            d3 = doc._get_alert_threshold('alert_days_3')
            if days <= d1 and not doc.alert_90_sent:
                doc._send_notification('alert_90')
                doc.alert_90_sent = True
            if days <= d2 and not doc.alert_30_sent:
                doc._send_notification('alert_30')
                doc.alert_30_sent = True
            if days <= d3 and not doc.alert_7_sent:
                doc._send_notification('alert_7')
                doc.alert_7_sent = True
            esc_days = doc.document_type_id.escalation_days if doc.document_type_id else 3
            if days < -esc_days and not doc.escalation_sent:
                doc._send_notification('escalation')
                doc.escalation_sent = True

    def _send_notification(self, alert_type):
        self.ensure_one()
        template_map = {
            'alert_90':   'smart_document_expiry.email_template_alert_90',
            'alert_30':   'smart_document_expiry.email_template_alert_30',
            'alert_7':    'smart_document_expiry.email_template_alert_7',
            'escalation': 'smart_document_expiry.email_template_escalation',
        }
        template = self.env.ref(template_map.get(alert_type, ''), raise_if_not_found=False)
        if template:
            try:
                template.send_mail(self.id, force_send=True)
                _logger.info('Document Expiry: sent %s alert for %s (id=%s)',
                             alert_type, self.name, self.id)
            except Exception as e:
                _logger.error('Document Expiry: failed to send alert: %s', e)

        label_map = {
            'alert_90':   f'⚠️ 90-day expiry alert sent — expires on {self.expiry_date}',
            'alert_30':   f'🟠 30-day expiry alert sent — expires on {self.expiry_date}',
            'alert_7':    f'🔴 Final 7-day alert sent — expires on {self.expiry_date}',
            'escalation': f'🚨 Escalation alert sent — document EXPIRED on {self.expiry_date}',
        }
        self.message_post(body=label_map.get(alert_type, 'Alert sent.'))

    # ─────────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────────

    def action_renew(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Renew Document'),
            'res_model': 'document.renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_document_id':      self.id,
                'default_name':             self.name,
                'default_document_type_id': self.document_type_id.id,
                'default_entity_type':      self.entity_type,
                'default_person_id':        self.person_id.id,
                'default_partner_id':       self.partner_id.id,
                'default_vehicle_id':       self.vehicle_id.id,
                'default_equipment_id':     self.equipment_id.id,
                'default_other_entity_name': self.other_entity_name,
                'default_responsible_id':   self.responsible_id.id,
            },
        }

    def action_archive_document(self):
        self.ensure_one()
        self.write({'state': 'archived'})
        self.message_post(body=_('Document archived.'))

    def action_view_history(self):
        self.ensure_one()
        ids = [self.id]
        doc = self
        while doc.previous_document_id:
            ids.append(doc.previous_document_id.id)
            doc = doc.previous_document_id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Document History'),
            'res_model': 'document.expiry',
            'view_mode': 'list,form',
            'domain': [('id', 'in', ids)],
        }

    def action_get_attachment_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }

    # ─────────────────────────────────────────────────────────────────────
    # Dashboard
    # ─────────────────────────────────────────────────────────────────────

    @api.model
    def get_dashboard_data(self):
        today = date.today()

        # ── Global counts ──────────────────────────────────────────────
        valid    = self.search_count([('state', '=', 'valid')])
        expiring = self.search_count([('state', '=', 'expiring_soon')])
        expired  = self.search_count([('state', '=', 'expired')])
        renewed  = self.search_count([('state', '=', 'renewed')])
        total    = valid + expiring + expired
        compliance = round((valid / total * 100) if total else 0, 1)

        # ── Critical: expiring within 7 days ──────────────────────────
        critical_count = self.search_count([
            ('state', 'not in', ['renewed', 'archived']),
            ('expiry_date', '!=', False),
            ('expiry_date', '<=', (today + __import__('datetime').timedelta(days=7)).strftime('%Y-%m-%d')),
            ('expiry_date', '>=', today.strftime('%Y-%m-%d')),
        ])

        # ── Breakdown by entity type ──────────────────────────────────
        entity_types = ['person', 'vendor', 'vehicle', 'equipment', 'other']
        entity_labels = {
            'person': 'Persons', 'vendor': 'Vendors',
            'vehicle': 'Vehicles', 'equipment': 'Equipment', 'other': 'Other',
        }
        entity_icons = {
            'person': 'fa-user', 'vendor': 'fa-building',
            'vehicle': 'fa-truck', 'equipment': 'fa-cog', 'other': 'fa-tag',
        }
        by_entity = []
        for et in entity_types:
            et_valid    = self.search_count([('entity_type', '=', et), ('state', '=', 'valid')])
            et_expiring = self.search_count([('entity_type', '=', et), ('state', '=', 'expiring_soon')])
            et_expired  = self.search_count([('entity_type', '=', et), ('state', '=', 'expired')])
            et_total    = et_valid + et_expiring + et_expired
            if et_total == 0:
                continue
            et_compliance = round(et_valid / et_total * 100, 0) if et_total else 100
            by_entity.append({
                'type':       et,
                'label':      entity_labels[et],
                'icon':       entity_icons[et],
                'valid':      et_valid,
                'expiring':   et_expiring,
                'expired':    et_expired,
                'total':      et_total,
                'compliance': int(et_compliance),
            })

        # ── Upcoming expirations (next 10, ordered by urgency) ────────
        upcoming_docs = self.search(
            [('state', 'in', ['valid', 'expiring_soon']),
             ('expiry_date', '!=', False)],
            order='expiry_date asc', limit=10
        )
        upcoming_data = []
        for d in upcoming_docs:
            days = (d.expiry_date - today).days
            entity_name = (
                d.person_id.name or d.partner_id.name or
                d.vehicle_id.name or d.equipment_id.name or
                d.other_entity_name or ''
            )
            upcoming_data.append({
                'id':           d.id,
                'name':         d.name,
                'entity_type':  d.entity_type,
                'entity_name':  entity_name,
                'doc_type':     d.document_type_id.name if d.document_type_id else '',
                'expiry_date':  d.expiry_date.strftime('%d/%m/%Y'),
                'days':         days,
                'state':        d.state,
                'responsible':  d.responsible_id.name if d.responsible_id else '',
            })

        # ── Recently expired (last 5 expired, not renewed) ────────────
        recently_expired = self.search(
            [('state', '=', 'expired'), ('expiry_date', '!=', False)],
            order='expiry_date desc', limit=5
        )
        expired_data = []
        for d in recently_expired:
            days_over = (today - d.expiry_date).days
            entity_name = (
                d.person_id.name or d.partner_id.name or
                d.vehicle_id.name or d.equipment_id.name or
                d.other_entity_name or ''
            )
            expired_data.append({
                'id':          d.id,
                'name':        d.name,
                'entity_type': d.entity_type,
                'entity_name': entity_name,
                'expiry_date': d.expiry_date.strftime('%d/%m/%Y'),
                'days_over':   days_over,
                'responsible': d.responsible_id.name if d.responsible_id else '',
            })

        # ── Top 5 document types by count ────────────────────────────
        DocType = self.env['document.expiry.type']
        doc_types = DocType.search([])
        type_stats = []
        for dt in doc_types:
            cnt = self.search_count([('document_type_id', '=', dt.id),
                                     ('state', 'not in', ['renewed', 'archived'])])
            if cnt > 0:
                type_stats.append({'name': dt.name, 'count': cnt})
        type_stats.sort(key=lambda x: x['count'], reverse=True)
        top_types = type_stats[:5]

        # ── Alerts sent today (from chatter/log) — approximation ──────
        # Count docs where any alert was sent (flag is True)
        alerts_90 = self.search_count([('alert_90_sent', '=', True),
                                        ('state', 'not in', ['renewed', 'archived'])])
        alerts_30 = self.search_count([('alert_30_sent', '=', True),
                                        ('state', 'not in', ['renewed', 'archived'])])
        alerts_7  = self.search_count([('alert_7_sent',  '=', True),
                                        ('state', 'not in', ['renewed', 'archived'])])
        escalated = self.search_count([('escalation_sent', '=', True)])

        return {
            # KPIs
            'valid':          valid,
            'expiring':       expiring,
            'expired':        expired,
            'renewed':        renewed,
            'total':          total,
            'compliance':     compliance,
            'critical_count': critical_count,
            # Breakdowns
            'by_entity':      by_entity,
            'top_types':      top_types,
            # Tables
            'upcoming':       upcoming_data,
            'recently_expired': expired_data,
            # Alert stats
            'alerts': {
                'sent_90':    alerts_90,
                'sent_30':    alerts_30,
                'sent_7':     alerts_7,
                'escalated':  escalated,
            },
        }
