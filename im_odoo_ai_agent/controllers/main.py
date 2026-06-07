
import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class AiAgentController(http.Controller):


    @http.route('/ai_agent/config/status', type='jsonrpc', auth='user')
    def get_config_status(self):
        try:
            status = request.env['ai.agent.config'].get_status_for_controller()

            suggestions = request.env['ai.odoo.tool'].get_dynamic_suggestions()

            return {
                'success':         True,
                'gpt4all_available': status['gpt4all_available'],
                'model_name':      status['model_name'],
                'model_loaded':    status['model_loaded'],
                'status':          status['status'],
                'suggestions':     suggestions,
            }
        except Exception as e:
            _logger.error(f"[AI Agent] get_config_status error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/ai_agent/config/load_model', type='jsonrpc', auth='user')
    def load_model(self):
        try:
            config = request.env['ai.agent.config'].get_active_config()
            if not config:
                return {'success': False, 'error': "Aucune configuration IA active."}
            config.action_load_model()
            return {'success': True, 'message': f"Model {config.model_name} loaded."}
        except Exception as e:
            _logger.error(f"[AI Agent] load_model error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}


    @http.route('/ai_agent/session/create', type='jsonrpc', auth='user')
    def create_session(self):
        try:
            session = request.env['ai.chat.session'].create({
                'title':   'Nouvelle conversation',
                'user_id': request.env.uid,
            })
            return {
                'success':    True,
                'session_id': session.id,
                'title':      session.title,
            }
        except Exception as e:
            _logger.error(f"[AI Agent] create_session error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/ai_agent/session/list', type='jsonrpc', auth='user')
    def list_sessions(self):
        try:
            sessions = request.env['ai.chat.session'].search(
                [('user_id', '=', request.env.uid), ('active', '=', True)],
                order='is_pinned desc, write_date desc',
                limit=50,
            )
            return {
                'success':  True,
                'sessions': [
                    {
                        'id':            s.id,
                        'title':         s.title,
                        'is_pinned':     s.is_pinned,
                        'message_count': s.message_count,
                        'write_date':    s.write_date.isoformat() if s.write_date else '',
                    }
                    for s in sessions
                ],
            }
        except Exception as e:
            _logger.error(f"[AI Agent] list_sessions error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/ai_agent/session/messages', type='jsonrpc', auth='user')
    def get_session_messages(self, session_id):
        try:
            session = request.env['ai.chat.session'].browse(int(session_id))
            if not session.exists() or session.user_id.id != request.env.uid:
                return {'success': False, 'error': "Session not found or access denied."}
            return {'success': True, 'messages': session.get_messages_for_api()}
        except Exception as e:
            _logger.error(f"[AI Agent] get_session_messages error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/ai_agent/session/delete', type='jsonrpc', auth='user')
    def delete_session(self, session_id):
        try:
            session = request.env['ai.chat.session'].browse(int(session_id))
            if not session.exists() or session.user_id.id != request.env.uid:
                return {'success': False, 'error': "Session not found or access denied."}
            session.unlink()
            return {'success': True}
        except Exception as e:
            _logger.error(f"[AI Agent] delete_session error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/ai_agent/session/pin', type='jsonrpc', auth='user')
    def pin_session(self, session_id):
        try:
            session = request.env['ai.chat.session'].browse(int(session_id))
            if not session.exists():
                return {'success': False, 'error': "Session introuvable."}
            if session.user_id.id != request.env.uid:
                return {'success': False, 'error': "Access denied: this session does not belong to you."}
            session.write({'is_pinned': not session.is_pinned})
            return {'success': True, 'is_pinned': session.is_pinned}
        except Exception as e:
            _logger.error(f"[AI Agent] pin_session error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}


    @http.route('/ai_agent/chat/stream', type='http', auth='user', csrf=False)
    def stream_message(self, session_id, message, **kwargs):
        env         = request.env
        db          = env.cr.dbname
        uid         = env.uid
        context     = dict(env.context)

        try:
            session_id_int = int(session_id)
            session = env['ai.chat.session'].browse(session_id_int)
            if not session.exists() or session.user_id.id != uid:
                def _err():
                    yield 'data: {"type": "error", "content": "Session not found or access denied."}\n\n'.encode('utf-8')
                return Response(_err(), content_type='text/event-stream; charset=utf-8',
                                headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
                                direct_passthrough=True)

            config = env['ai.agent.config'].get_active_config()
            if not config:
                def _err():
                    yield b'data: {"type": "error", "content": "Aucune configuration IA active."}\n\n'
                return Response(_err(), content_type='text/event-stream; charset=utf-8',
                                headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
                                direct_passthrough=True)

            config_id         = config.id
            config_language   = config.language
            config_system_prompt = config.system_prompt
            ollama_url        = config.ollama_url
            ollama_model      = config.ollama_model
            backend           = config.backend
            temperature       = config.temperature
            top_p             = config.top_p
            max_tokens        = config.max_tokens

        except Exception as e:
            _logger.error(f"[AI Agent] stream_message init error: {e}", exc_info=True)
            def _err():
                payload = json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)
                yield f'data: {payload}\n\n'.encode('utf-8')
            return Response(_err(), content_type='text/event-stream; charset=utf-8',
                            headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
                            direct_passthrough=True)

        msg = (message or '').strip()

        def generate():
            def send(event_type, content='', **extra):
                payload = json.dumps({'type': event_type, 'content': content, **extra},
                                     ensure_ascii=False)
                return f'data: {payload}\n\n'.encode('utf-8')

            def new_env():
                from odoo.modules.registry import Registry as odoo_registry
                from odoo.api import Environment
                cr2 = odoo_registry(db).cursor()
                return cr2, Environment(cr2, uid, context)

            def orm_save_user_msg():
                cr2, e2 = new_env()
                try:
                    e2['ai.chat.message'].create({
                        'session_id': session_id_int, 'role': 'user', 'content': msg,
                    })
                    cr2.commit()
                finally:
                    cr2.close()

            def orm_classify():
                cr2, e2 = new_env()
                try:
                    return e2['ai.odoo.tool']._classify_question(msg)
                finally:
                    cr2.close()

            def orm_prepare_plan(candidate_models):
                cr2, e2 = new_env()
                try:
                    tool2   = e2['ai.odoo.tool']
                    config2 = e2['ai.agent.config'].browse(config_id)
                    schema  = tool2._get_candidate_schema(candidate_models)
                    plan    = tool2._planning_step(msg, schema, config2, candidate_models=candidate_models)
                    if plan['success']:
                        odoo_schema   = tool2._get_schema_for_models(plan['models'])
                        planning_note = tool2._build_planning_note(plan, None)
                    else:
                        odoo_schema   = schema
                        planning_note = tool2._build_aggregate_hint(False)
                    history = tool2._build_history_block(
                        e2['ai.chat.session'].browse(session_id_int), max_turns=4)
                    return plan, odoo_schema, planning_note, history
                finally:
                    cr2.close()

            def orm_execute_tool(tool_name, tool_args):
                cr2, e2 = new_env()
                try:
                    return e2['ai.odoo.tool'].execute_tool_call(tool_name, tool_args)
                finally:
                    cr2.close()

            def orm_extract_tool_calls(llm_response):
                cr2, e2 = new_env()
                try:
                    return e2['ai.odoo.tool']._extract_tool_calls(llm_response)
                finally:
                    cr2.close()

            def orm_clean_response(text):
                cr2, e2 = new_env()
                try:
                    return e2['ai.odoo.tool']._clean_response(text)
                finally:
                    cr2.close()

            def orm_build_sources(all_tool_calls, all_tool_results):
                cr2, e2 = new_env()
                try:
                    return e2['ai.odoo.tool']._build_sources_summary(all_tool_calls, all_tool_results)
                finally:
                    cr2.close()

            def orm_save_assistant_msg(final_clean, sources):
                cr2, e2 = new_env()
                try:
                    e2['ai.chat.message'].create({
                        'session_id': session_id_int,
                        'role':       'assistant',
                        'content':    final_clean,
                        'sources':    sources,
                    })
                    session2 = e2['ai.chat.session'].browse(session_id_int)
                    if session2.message_count <= 2:
                        title = msg[:50] + ('...' if len(msg) > 50 else '')
                        session2.write({'title': title})
                    cr2.commit()
                finally:
                    cr2.close()

            def get_streaming_generator(prompt):
                import requests as _requests
                url      = (ollama_url or 'http://localhost:11434').rstrip('/')
                payload  = {
                    'model':  ollama_model or 'llama3',
                    'prompt': prompt,
                    'stream': True,
                    'options': {
                        'temperature': temperature,
                        'top_p':       top_p,
                        'num_predict': max_tokens,
                    },
                }
                try:
                    with _requests.post(f"{url}/api/generate", json=payload,
                                        timeout=300, stream=True) as r:
                        r.raise_for_status()
                        for line in r.iter_lines():
                            if not line:
                                continue
                            try:
                                data  = json.loads(line.decode('utf-8'))
                                token = data.get('response', '')
                                if token:
                                    yield token
                                if data.get('done'):
                                    break
                            except Exception:
                                continue
                except Exception as e:
                    _logger.error(f"[AI Agent] Ollama streaming error: {e}")
                    yield f"\n[Erreur Ollama : {e}]"

            try:
                orm_save_user_msg()

                yield send('step', '🔍 Analyse de votre question...')
                intent = orm_classify()

                from datetime import date
                lang = {'fr': 'Always respond in French.',
                        'en': 'Always respond in English.',
                        'ar': 'Always respond in Arabic.'}.get(config_language, 'Always respond in English.')

                if intent['is_chitchat']:
                    yield send('step', '💬 Preparing the response...')
                    prompt = (f"{config_system_prompt}\n{lang}\n\n"
                              f"Date : {date.today().isoformat()}\n\n"
                              f"Utilisateur : {msg}\n\nAssistant:")
                    full_response = ''
                    for token in get_streaming_generator(prompt):
                        full_response += token
                        yield send('token', token)
                    clean = orm_clean_response(full_response)
                    orm_save_assistant_msg(clean, '')
                    yield send('done', '', sources='')
                    return

                candidate_models = intent.get('candidate_models', [])
                if candidate_models:
                    yield send('step', f'📋 Models detected: {", ".join(candidate_models)}')

                yield send('step', '🗂️ Identifying required data...')
                try:
                    plan, odoo_schema, planning_note, history_block = orm_prepare_plan(candidate_models)
                except Exception as plan_err:
                    _logger.error(f"[AI Agent] Planning error: {plan_err}", exc_info=True)
                    yield send('error', f'Erreur lors du planning : {plan_err}')
                    return

                if plan['success']:
                    yield send('step', f'📋 Models: {", ".join(plan["models"])}')
                    for mn, fl in plan.get("fields_map", {}).items():
                        preview = ", ".join(fl[:4]) + ("..." if len(fl) > 4 else "")
                        yield send('step', f'   └─ {mn} → {preview}')
                else:
                    yield send('step', '⚠️ Planning failed, using default schema')

                lang_labels = {'fr': 'Always respond in French.',
                               'en': 'Always respond in English.',
                               'ar': 'أجب دائماً باللغة العربية.'}
                system_prompt = f"""{config_system_prompt}
{lang_labels.get(config_language, lang_labels['fr'])}

=== SYSTÈME D'ACCÈS AUX DONNÉES ODOO ===
Date aujourd'hui : {date.today().isoformat()}
{planning_note}

You are an agent that MUST use tools to answer questions about the data.
ABSOLUTE RULE: You must NEVER invent or assume data. You MUST always execute a tool.
ABSOLUTE RULE: To execute a tool, you MUST write exactly "TOOL_CALL:" followed by JSON on the same line.
ABSOLUTE RULE: Do not explain what you are going to do. Execute the tool directly.

--- FORMAT OBLIGATOIRE POUR EXÉCUTER UN OUTIL ---
TOOL_CALL: {{"tool": "NOM_OUTIL", "args": {{...}}}}

--- OUTILS DISPONIBLES ---
TOOL_CALL: {{"tool": "search_records", "args": {{"model": "MODEL", "domain": [["champ", "op", "val"]], "fields": ["champ1", "champ2"], "limit": 20, "order": "champ desc"}}}}
TOOL_CALL: {{"tool": "aggregate_records", "args": {{"model": "MODEL", "domain": [...], "fields": ["champ:sum", "id:count"], "groupby": ["champ_groupby"]}}}}
TOOL_CALL: {{"tool": "get_record_count", "args": {{"model": "MODEL", "domain": [...]}}}}

--- EXEMPLES OBLIGATOIRES À SUIVRE ---

Question: "Combien de commandes aujourd'hui ?"
Correct response:
TOOL_CALL: {{"tool": "get_record_count", "args": {{"model": "sale.order", "domain": [["date_order", ">=", "{date.today().isoformat()} 00:00:00"], ["date_order", "<=", "{date.today().isoformat()} 23:59:59"]]}}}}

Question: "Liste des clients"
Correct response:
TOOL_CALL: {{"tool": "search_records", "args": {{"model": "res.partner", "domain": [["customer_rank", ">", 0]], "fields": ["name", "email", "phone"], "limit": 20}}}}

Question: "Chiffre d'affaires du mois"
Correct response:
TOOL_CALL: {{"tool": "aggregate_records", "args": {{"model": "sale.order", "domain": [["state", "in", ["sale", "done"]], ["date_order", ">=", "{date.today().replace(day=1).isoformat()}"]], "fields": ["amount_total:sum"], "groupby": []}}}}

--- SCHÉMA DES MODÈLES DISPONIBLES ---
{odoo_schema}

--- RAPPEL FINAL ---
Start IMMEDIATELY with TOOL_CALL: to retrieve data. Say nothing before.
"""
                messages_list = []
                if history_block:
                    messages_list.append({'role': 'user',      'content': f'[Historique]\n{history_block}'})
                    messages_list.append({'role': 'assistant', 'content': 'Compris.'})
                messages_list.append({'role': 'user', 'content': msg})

                all_tool_calls   = []
                all_tool_results = []
                final_response   = ''

                for iteration in range(1, 7):
                    full_prompt = system_prompt + '\n\n'
                    for m in messages_list:
                        label = 'Question' if m['role'] == 'user' else 'Assistant'
                        full_prompt += f"{label}: {m['content']}\n\n"
                    full_prompt += 'Assistant:'

                    llm_response      = ''
                    in_tool_call      = False
                    sent_thinking     = False

                    for token in get_streaming_generator(full_prompt):
                        llm_response += token
                        if 'TOOL_CALL:' in llm_response and not in_tool_call:
                            in_tool_call = True
                            if not sent_thinking:
                                yield send('thinking_start')
                                sent_thinking = True
                        if not in_tool_call:
                            yield send('token', token)
                            final_response += token

                    if in_tool_call:
                        yield send('thinking_end')

                    tool_calls_found = orm_extract_tool_calls(llm_response)

                    if not tool_calls_found:
                        if in_tool_call:
                            cleaned = orm_clean_response(llm_response)
                            for ch in cleaned:
                                yield send('token', ch)
                            final_response = cleaned
                        break

                    tool_results_text = []
                    for tc in tool_calls_found:
                        tool_name  = tc.get('tool', '')
                        tool_args  = tc.get('args', {})
                        model_name = tool_args.get('model', tool_name)
                        all_tool_calls.append(tc)
                        yield send('step', f'🔧 Executing: {tool_name}({model_name})')
                        result = orm_execute_tool(tool_name, tool_args)
                        all_tool_results.append(result)
                        summary = result.split('\n')[0] if result else ''
                        yield send('step', f'   ✅ {summary}')
                        tool_results_text.append(f"Result {tool_name}({model_name}):\n{result}")

                    messages_list.append({'role': 'assistant', 'content': llm_response})
                    messages_list.append({
                        'role': 'user',
                        'content': (
                            f"RÉSULTATS DES OUTILS:\n{chr(10).join(tool_results_text)}\n\n"
                            "Now provide your final answer to the user."
                        ),
                    })
                    in_tool_call = False
                    yield send('step', f'💭 Iteration {iteration} — building the response...')

                final_clean = orm_clean_response(final_response) if final_response else \
                              "I analyzed the data but could not formulate a response. Please reformulez ?"
                sources = orm_build_sources(all_tool_calls, all_tool_results)
                orm_save_assistant_msg(final_clean, sources)
                yield send('done', '', sources=sources)

            except Exception as e:
                _logger.error(f"[AI Agent] stream_message error: {e}", exc_info=True)
                yield send('error', str(e))

        return Response(
            generate(),
            content_type='text/event-stream; charset=utf-8',
            headers={
                'Cache-Control':     'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection':        'keep-alive',
            },
            direct_passthrough=True,
        )