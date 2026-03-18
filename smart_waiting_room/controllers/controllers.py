# -*- coding: utf-8 -*-
import json
import os
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WaitingRoomDisplay(http.Controller):

    # ── TV Display ────────────────────────────────────────────────────────────

    @http.route('/waiting-room/display/<string:token>',
                type='http', auth='public', website=False, csrf=False)
    def display_screen(self, token, **kwargs):
        room = request.env['waiting.room'].sudo().search(
            [('display_token', '=', token)], limit=1)
        if not room:
            return request.not_found()

        # Read the standalone HTML file directly
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'src', 'display.html'
        )
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except Exception as e:
            _logger.error("display.html not found: %s", e)
            return request.not_found()

        # Inject room data as JSON into the page
        room_data = json.dumps({
            'token': token,
            'room_name': room.name,
            'welcome_message': room.welcome_message or 'Welcome',
            'footer_message': room.footer_message or 'Thank you for your patience',
            'audio_enabled': room.audio_enabled,
            'show_estimated_time': room.show_estimated_time,
        }, ensure_ascii=False)

        html = html.replace('__ROOM_DATA__', room_data)

        return request.make_response(html.encode('utf-8'), headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ])

    # ── Kiosk ─────────────────────────────────────────────────────────────────

    @http.route('/waiting-room/kiosk/<string:token>',
                type='http', auth='public', website=False, csrf=False)
    def kiosk_screen(self, token, **kwargs):
        room = request.env['waiting.room'].sudo().search(
            [('display_token', '=', token)], limit=1)
        if not room:
            return request.not_found()

        html_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'src', 'kiosk.html'
        )
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except Exception as e:
            _logger.error("kiosk.html not found: %s", e)
            return request.not_found()

        depts_data = [
            {
                'id': d.id,
                'name': d.name,
                'icon': d.icon or 'fa-plus',
                'color': d.display_color or '#3b82f6',
                'wait': d.avg_service_duration,
            }
            for d in room.department_ids
        ]
        room_data = json.dumps({
            'token': token,
            'room_name': room.name,
            'welcome_message': room.welcome_message or 'Welcome',
            'departments': depts_data,
        }, ensure_ascii=False)

        html = html.replace('__ROOM_DATA__', room_data)

        return request.make_response(html.encode('utf-8'), headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ])

    # ── Queue API — HTTP (not JSON-RPC) ───────────────────────────────────────
    # Using type='http' avoids Odoo's JSON-RPC envelope which complicates the JS

    @http.route('/waiting-room/api/queue/<string:token>',
                type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def get_queue_data(self, token, **kwargs):
        room = request.env['waiting.room'].sudo().search(
            [('display_token', '=', token)], limit=1)
        if not room:
            data = json.dumps({'error': 'Room not found'})
            return request.make_response(data, headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
            ])

        lines = request.env['waiting.room.line'].sudo().search([
            ('room_id', '=', room.id),
            ('state', 'in', ['waiting', 'called', 'in_service']),
            ('active', '=', True),
        ], order='priority desc, sequence asc, token_number asc')

        def to_dict(l):
            return {
                'id': l.id,
                'token': l.token_display or ('T%03d' % l.token_number),
                'name': l.name or '',
                'state': l.state,
                'priority': l.priority or '0',
                'department': l.department_id.name if l.department_id else '',
                'dept_color': l.department_id.display_color if l.department_id else '#4f8ef7',
                'estimated_wait': int(l.estimated_wait or 0),
                'wait_duration': round(float(l.wait_duration or 0), 1),
                'is_late': bool(l.is_late),
                'call_count': int(l.call_count or 0),
                # partner info — not used by TV/kiosk, available for future staff widgets
                'partner_id': l.partner_id.id if l.partner_id else None,
            }

        current = lines.filtered(lambda l: l.state == 'in_service')
        called  = lines.filtered(lambda l: l.state == 'called')
        waiting = lines.filtered(lambda l: l.state == 'waiting')

        done_count = request.env['waiting.room.line'].sudo().search_count([
            ('room_id', '=', room.id),
            ('state', '=', 'done'),
            ('active', 'in', [True, False]),
        ])

        result = {
            'room_name': room.name or '',
            'welcome_message': room.welcome_message or 'Welcome',
            'footer_message': room.footer_message or 'Thank you for your patience',
            'ticker_messages': room.ticker_messages or 'Thank you for your patience.',
            'is_open': bool(room.is_open),
            'audio_enabled': bool(room.audio_enabled),
            'show_estimated_time': bool(room.show_estimated_time),
            'show_visitor_name': bool(room.show_visitor_name),
            'current': [to_dict(l) for l in current],
            'called':  [to_dict(l) for l in called],
            'waiting': [to_dict(l) for l in waiting[:20]],
            'total_waiting': len(waiting),
            'done_today': done_count,
            'avg_wait': round(float(room.avg_wait_time or 0), 1),
        }

        data = json.dumps(result, ensure_ascii=False)
        return request.make_response(data.encode('utf-8'), headers=[
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Access-Control-Allow-Origin', '*'),
            ('Cache-Control', 'no-cache'),
        ])

    # ── Kiosk Check-in API — HTTP ─────────────────────────────────────────────

    @http.route('/waiting-room/api/checkin/<string:token>',
                type='http', auth='public', methods=['POST'], csrf=False)
    def kiosk_checkin(self, token, **kwargs):
        try:
            body = request.httprequest.get_data(as_text=True)
            params = json.loads(body) if body else {}
        except Exception:
            params = {}

        name         = (params.get('name') or '').strip()
        phone        = (params.get('phone') or '').strip()
        notes        = (params.get('notes') or '').strip()
        dept_id      = params.get('department_id')
        visitor_type = params.get('visitor_type') or 'walk_in'

        if not name:
            data = json.dumps({'error': 'Name is required'})
            return request.make_response(data, headers=[('Content-Type', 'application/json')])

        room = request.env['waiting.room'].sudo().search(
            [('display_token', '=', token)], limit=1)
        if not room:
            data = json.dumps({'error': 'Room not found'})
            return request.make_response(data, headers=[('Content-Type', 'application/json')])

        if not room.is_open:
            data = json.dumps({'error': 'Room is currently closed'})
            return request.make_response(data, headers=[('Content-Type', 'application/json')])

        vals = {
            'room_id': room.id,
            'name': name,
            'phone': phone,
            'notes': notes,
            'visitor_type': visitor_type,
        }
        if dept_id:
            try:
                dept = request.env['waiting.room.department'].sudo().browse(int(dept_id))
                if dept.exists():
                    vals['department_id'] = dept.id
            except Exception:
                pass

        line = request.env['waiting.room.line'].sudo().create(vals)

        position = request.env['waiting.room.line'].sudo().search_count([
            ('room_id', '=', room.id),
            ('state', '=', 'waiting'),
            ('token_number', '<', line.token_number),
        ]) + 1

        result = {
            'success': True,
            'token': line.token_display or ('T%03d' % line.token_number),
            'name': line.name,
            'department': line.department_id.name if line.department_id else '',
            'estimated_wait': int(line.estimated_wait or 0),
            'position': position,
        }
        data = json.dumps(result, ensure_ascii=False)
        return request.make_response(data.encode('utf-8'), headers=[
            ('Content-Type', 'application/json; charset=utf-8'),
        ])

    # ── User Manual ───────────────────────────────────────────────────────────

    @http.route('/waiting-room/manual',
                type='http', auth='user', website=False, csrf=False)
    def user_manual(self, **kwargs):
        manual_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'user_manual.html'
        )
        try:
            with open(manual_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Inject the Odoo user's language so the manual auto-selects it
            # request.env.user.lang returns e.g. 'en_US', 'fr_FR', 'ar_SA'
            user_lang = 'en'
            try:
                odoo_lang = request.env.user.lang or 'en_US'
                # Map Odoo lang codes → manual lang keys
                lang_map = {
                    'en': 'en', 'fr': 'fr', 'ar': 'ar',
                    'es': 'es', 'de': 'de', 'pt': 'pt',
                    'zh': 'zh',
                }
                prefix = odoo_lang.split('_')[0].lower()
                user_lang = lang_map.get(prefix, 'en')
            except Exception:
                user_lang = 'en'

            # Replace the placeholder in detectLang() with the actual Odoo lang
            content = content.replace(
                'var ODOO_LANG = null;',
                'var ODOO_LANG = "%s";' % user_lang
            )

            return request.make_response(content.encode('utf-8'), headers=[
                ('Content-Type', 'text/html; charset=utf-8'),
            ])
        except Exception:
            return request.not_found()
