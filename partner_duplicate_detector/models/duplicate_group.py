# -*- coding: utf-8 -*-
import unicodedata
import re
from difflib import SequenceMatcher
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


def _normalize(text):
    """Normalize a string for comparison: lowercase, no accents, no punctuation."""
    if not text:
        return ''
    text = text.lower().strip()
    # Remove accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    # Remove punctuation and extra spaces
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _normalize_phone(phone):
    """Normalize phone: keep digits only."""
    if not phone:
        return ''
    return re.sub(r'\D', '', phone)


def _normalize_email(email):
    """Normalize email: lowercase."""
    if not email:
        return ''
    return email.lower().strip()


def _similarity(a, b):
    """Return similarity ratio between 0 and 1."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


class DuplicateGroup(models.Model):
    _name = 'partner.duplicate.group'
    _description = 'Group of Duplicate Partners'
    _order = 'score desc, id desc'

    name = fields.Char(
        string='Group Name',
        compute='_compute_name',
        store=True,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'partner_duplicate_group_rel',
        'group_id',
        'partner_id',
        string='Duplicate Partners',
    )
    partner_count = fields.Integer(
        string='Duplicates',
        compute='_compute_partner_count',
        store=True,
    )
    score = fields.Float(
        string='Similarity Score (%)',
        digits=(5, 1),
        help='How similar these partners are (0–100%)',
    )
    reason = fields.Char(string='Match Reason')
    state = fields.Selection([
        ('pending', 'To Review'),
        ('merged', 'Merged'),
        ('ignored', 'Ignored'),
    ], default='pending', string='Status', index=True)
    master_partner_id = fields.Many2one(
        'res.partner',
        string='Master Record',
        help='The partner record that will be kept after merge.',
    )

    @api.depends('partner_ids')
    def _compute_name(self):
        for rec in self:
            names = rec.partner_ids.mapped('name')
            rec.name = ' / '.join(names[:2]) if names else _('Unnamed Group')

    @api.depends('partner_ids')
    def _compute_partner_count(self):
        for rec in self:
            rec.partner_count = len(rec.partner_ids)

    def action_ignore(self):
        self.write({'state': 'ignored'})

    def action_review(self):
        self.write({'state': 'pending'})

    def action_open_merge_wizard(self):
        self.ensure_one()
        if not self.partner_ids:
            raise UserError(_('No partners in this group.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Merge Duplicate Partners'),
            'res_model': 'merge.partner.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_group_id': self.id,
                'default_partner_ids': self.partner_ids.ids,
                'default_master_partner_id': (
                    self.master_partner_id.id or self.partner_ids[:1].id
                ),
            },
        }

    # ------------------------------------------------------------------
    # SCANNING ENGINE
    # ------------------------------------------------------------------

    @api.model
    def run_scan(self):
        """
        Main scan method. Called on install and by weekly cron.
        Detects duplicates by:
          1. Exact email match
          2. Exact phone match (normalized)
          3. Exact VAT match
          4. High name similarity (>= 85%)
        Creates DuplicateGroup records for new groups found.
        """
        _logger.info('Partner Duplicate Detector: starting scan...')
        Partner = self.env['res.partner']
        all_partners = Partner.search([
            ('active', '=', True),
            ('type', '=', 'contact'),
        ])
        _logger.info('Scanning %d partners...', len(all_partners))

        found_pairs = {}  # key: frozenset of ids -> (score, reason)

        # --- Pass 1: Exact email ---
        email_map = {}
        for p in all_partners:
            key = _normalize_email(p.email)
            if key:
                email_map.setdefault(key, []).append(p)
        for key, partners in email_map.items():
            if len(partners) > 1:
                for i in range(len(partners)):
                    for j in range(i + 1, len(partners)):
                        pair = frozenset([partners[i].id, partners[j].id])
                        if pair not in found_pairs or found_pairs[pair][0] < 100:
                            found_pairs[pair] = (100.0, _('Identical email'))

        # --- Pass 2: Exact phone ---
        phone_map = {}
        for p in all_partners:
            for phone_val in [p.phone]:
                key = _normalize_phone(phone_val)
                if key and len(key) >= 7:
                    phone_map.setdefault(key, []).append(p)
        for key, partners in phone_map.items():
            unique = list({p.id: p for p in partners}.values())
            if len(unique) > 1:
                for i in range(len(unique)):
                    for j in range(i + 1, len(unique)):
                        pair = frozenset([unique[i].id, unique[j].id])
                        if pair not in found_pairs:
                            found_pairs[pair] = (95.0, _('Identical phone number'))

        # --- Pass 3: Exact VAT ---
        vat_map = {}
        for p in all_partners:
            key = (p.vat or '').strip().upper()
            if key:
                vat_map.setdefault(key, []).append(p)
        for key, partners in vat_map.items():
            if len(partners) > 1:
                for i in range(len(partners)):
                    for j in range(i + 1, len(partners)):
                        pair = frozenset([partners[i].id, partners[j].id])
                        if pair not in found_pairs:
                            found_pairs[pair] = (98.0, _('Identical VAT number'))

        # --- Pass 4: Name similarity ---
        partner_list = [(p, _normalize(p.name)) for p in all_partners if p.name]
        threshold = 0.85
        for i in range(len(partner_list)):
            for j in range(i + 1, len(partner_list)):
                p1, n1 = partner_list[i]
                p2, n2 = partner_list[j]
                pair = frozenset([p1.id, p2.id])
                if pair in found_pairs:
                    continue  # already detected by a stronger signal
                sim = _similarity(n1, n2)
                if sim >= threshold:
                    score = round(sim * 100, 1)
                    found_pairs[pair] = (score, _('Very similar name (%.0f%%)') % score)

        _logger.info('Found %d potential duplicate pairs.', len(found_pairs))

        # --- Build groups from pairs (union-find) ---
        parent = {}

        def find(x):
            while parent.get(x, x) != x:
                parent[x] = parent.get(parent.get(x, x), x)
                x = parent.get(x, x)
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        pair_data = {}
        for pair, (score, reason) in found_pairs.items():
            ids = list(pair)
            union(ids[0], ids[1])
            pair_data[pair] = (score, reason)

        groups = {}
        for pair, (score, reason) in pair_data.items():
            ids = list(pair)
            root = find(ids[0])
            if root not in groups:
                groups[root] = {'ids': set(), 'score': 0, 'reason': reason}
            groups[root]['ids'].update(ids)
            if score > groups[root]['score']:
                groups[root]['score'] = score
                groups[root]['reason'] = reason

        # --- Persist new groups (skip already existing ones) ---
        existing_groups = self.search([('state', 'in', ['pending', 'ignored'])])
        existing_sets = []
        for eg in existing_groups:
            existing_sets.append(frozenset(eg.partner_ids.ids))

        created = 0
        for root, data in groups.items():
            group_set = frozenset(data['ids'])
            if group_set in existing_sets:
                continue
            if len(data['ids']) < 2:
                continue
            self.create({
                'partner_ids': [(6, 0, list(data['ids']))],
                'score': data['score'],
                'reason': data['reason'],
                'state': 'pending',
                'master_partner_id': min(data['ids']),  # oldest record
            })
            created += 1

        _logger.info('Partner Duplicate Detector: %d new groups created.', created)
        action = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Duplicate Detector',
                    'message': 'Scan complete! %d new duplicate group(s) found.' % created,
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window',
                        'name': 'Duplicate Partners',
                        'res_model': 'partner.duplicate.group',
                        'view_mode': 'list,form',
                        'context': {'search_default_pending': 1},
                    },
                },
            }
        return created

    @api.model
    def get_dashboard_data(self):
        """Return stats for the dashboard."""
        total_pending = self.search_count([('state', '=', 'pending')])
        total_merged = self.search_count([('state', '=', 'merged')])
        total_ignored = self.search_count([('state', '=', 'ignored')])
        # Partners affected
        pending_groups = self.search([('state', '=', 'pending')])
        affected = len(set(
            pid
            for g in pending_groups
            for pid in g.partner_ids.ids
        ))
        return {
            'pending': total_pending,
            'merged': total_merged,
            'ignored': total_ignored,
            'affected_partners': affected,
        }
