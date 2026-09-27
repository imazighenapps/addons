from datetime import timedelta

from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fs_duplicate_match_count = fields.Integer(compute='_compute_fs_duplicate_match_count')
    fs_duplicate_warning = fields.Boolean(compute='_compute_fs_duplicate_match_count')

    def _compute_fs_duplicate_match_count(self):
        Match = self.env['fs.sale.order.duplicate.match']
        grouped = Match._read_group(
            [('sale_order_id', 'in', self.ids), ('state', '=', 'open')],
            ['sale_order_id'],
            ['__count'],
        )
        counts = {order.id: count for order, count in grouped}
        for order in self:
            order.fs_duplicate_match_count = counts.get(order.id, 0)
            order.fs_duplicate_warning = bool(order.fs_duplicate_match_count)

    def _fs_refresh_duplicate_matches(self):
        service = self.env['fs.sale.order.duplicate.mixin']
        Match = self.env['fs.sale.order.duplicate.match']
        Config = self.env['fs.sale.order.duplicate.config'].sudo()
        for order in self:
            cfg = Config.search(
                [('company_id', '=', order.company_id.id), ('active', '=', True)],
                limit=1,
            )
            if not cfg or not order.partner_id or not order.date_order:
                continue
            domain = [
                ('id', '<', order.id),
                ('partner_id', '=', order.partner_id.id),
                ('company_id', '=', order.company_id.id),
                ('date_order', '>=', order.date_order - timedelta(days=cfg.lookback_days)),
                ('state', 'not in', ('cancel',)),
            ]
            candidates = self.search(domain, order='date_order desc', limit=50)
            existing = Match.search([('sale_order_id', '=', order.id)])
            existing_by_candidate = {match.candidate_order_id.id: match for match in existing}
            seen_candidate_ids = set()
            for candidate in candidates:
                score, factors = service._score_orders(order, candidate, cfg)
                if score < cfg.medium_threshold:
                    continue
                seen_candidate_ids.add(candidate.id)
                values = {
                    'sale_order_id': order.id,
                    'candidate_order_id': candidate.id,
                    'company_id': order.company_id.id,
                    'score': score,
                    'level': 'likely' if score >= cfg.high_threshold else 'possible',
                    'factors': '\n'.join(factors),
                    'state': 'open',
                    'decision_note': False,
                    'decided_by': False,
                    'decision_date': False,
                }
                match = existing_by_candidate.get(candidate.id)
                if match:
                    match.with_context(fs_duplicate_internal=True).write(values)
                else:
                    Match.with_context(fs_duplicate_internal=True).create(values)
            stale = existing.filtered(
                lambda rec: rec.state == 'open' and rec.candidate_order_id.id not in seen_candidate_ids
            )
            stale.with_context(fs_duplicate_internal=True).write({
                'state': 'ignored',
                'decision_note': _('No longer above the configured threshold.'),
                'decided_by': self.env.user.id,
                'decision_date': fields.Datetime.now(),
            })
        return True

    def action_confirm(self):
        if not self.env.context.get('fs_duplicate_override'):
            self._fs_refresh_duplicate_matches()
            self.invalidate_recordset(['fs_duplicate_match_count', 'fs_duplicate_warning'])
            blocked = self.filtered(lambda order: order.fs_duplicate_match_count)
            if blocked:
                return blocked[0].action_fs_duplicate_review_wizard()
        return super().action_confirm()

    def action_fs_duplicate_check(self):
        self._fs_refresh_duplicate_matches()
        self.invalidate_recordset(['fs_duplicate_match_count', 'fs_duplicate_warning'])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Duplicate Reviews'),
            'res_model': 'fs.sale.order.duplicate.match',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', 'in', self.ids), ('state', '=', 'open')],
            'target': 'current',
        }

    def action_fs_duplicate_review_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Review Possible Duplicate Orders'),
            'res_model': 'fs.sale.order.duplicate.review.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }
