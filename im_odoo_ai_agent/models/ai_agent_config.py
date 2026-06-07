
import json
import logging
import threading
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    _logger.info("[AI Agent] GPT4All not installed (pip install gpt4all). Ollama backend still available.")

OLLAMA_DEFAULT_URL = 'http://localhost:11434'


class AiAgentConfig(models.Model):
    _name        = 'ai.agent.config'
    _description = 'AI Agent Configuration'
    _rec_name    = 'name'

    name   = fields.Char(string='Name', required=True, default='Main AI Agent')
    active = fields.Boolean(default=True)

    backend = fields.Selection([
        ('gpt4all',      'GPT4All (local en mémoire)'),
        ('ollama',       'Ollama (serveur HTTP local)'),
        ('openai',       'OpenAI (ChatGPT)'),
        ('anthropic',    'Anthropic (Claude)'),
        ('gemini',       'Google Gemini'),
        ('openai_compat','API compatible OpenAI (Mistral, Groq, etc.)'),
    ], string='Backend IA', default='gpt4all', required=True,
       help="GPT4All : modèle local en mémoire.\n"
            "Ollama : serveur local HTTP.\n"
            "OpenAI / Anthropic / Gemini : API cloud (clé API requise).\n"
            "OpenAI compat : tout service compatible OpenAI (Mistral AI, Groq, Together, etc.).")

    api_key = fields.Char(
        string='Clé API',
        help="Clé API pour OpenAI, Anthropic (Claude) ou Google Gemini.\n"
             "Stockée de façon sécurisée dans la base de données.",
    )
    api_model = fields.Char(
        string='Modèle API',
        default='gpt-4o-mini',
        help="Nom du modèle à utiliser.\n"
             "OpenAI : gpt-4o, gpt-4o-mini, gpt-4-turbo\n"
             "Anthropic : claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001\n"
             "Gemini : gemini-2.0-flash, gemini-1.5-pro\n"
             "Groq : llama3-70b-8192, mixtral-8x7b-32768",
    )
    api_base_url = fields.Char(
        string='URL de base API (OpenAI compat)',
        help="Pour les backends compatibles OpenAI :\n"
             "Mistral : https://api.mistral.ai/v1\n"
             "Groq    : https://api.groq.com/openai/v1\n"
             "Together: https://api.together.xyz/v1\n"
             "Laissez vide pour OpenAI officiel.",
    )

    model_name = fields.Char(
        string='Modèle GPT4All (.gguf)',
        default='Meta-Llama-3-8B-Instruct.Q4_0.gguf',
        help="Nom du fichier .gguf. Utilisé uniquement si backend = GPT4All.",
    )
    model_path = fields.Char(
        string='Chemin des modèles GPT4All',
        default='/root/.local/share/nomic.ai/GPT4All/',
        help="Répertoire contenant les fichiers .gguf.",
    )
    device = fields.Selection([
        ('cpu',   'CPU'),
        ('gpu',   'GPU (CUDA)'),
        ('metal', 'Apple Metal'),
    ], default='cpu', string='Dispositif (GPT4All)')
    n_threads = fields.Integer(string='Threads CPU (GPT4All)', default=4)
    n_ctx     = fields.Integer(
        string='Fenêtre de contexte (tokens)',
        default=4096,
        help='GPT4All : taille max du contexte. Llama 3 8B = 8192, Mistral 7B = 4096.\n'
             'Ollama : géré automatiquement par le serveur.',
    )

    ollama_url = fields.Char(
        string='URL serveur Ollama',
        default=OLLAMA_DEFAULT_URL,
        help="URL du serveur Ollama. Défaut : http://localhost:11434\n"
             "Pour un serveur distant : http://192.168.1.x:11434",
    )
    ollama_model = fields.Char(
        string='Modèle Ollama',
        default='llama3',
        help="Nom du modèle tel qu'il apparaît dans `ollama list`.\n"
             "Exemples : llama3, llama3:8b, mistral, phi3, codellama, gemma2",
    )

    max_tokens  = fields.Integer(string='Tokens max',    default=1024)
    temperature = fields.Float(string='Température',     default=0.7)
    top_p       = fields.Float(string='Top P',           default=0.9)

    language = fields.Selection([
        ('fr', 'French'),
        ('en', 'English'),
        ('ar', 'العربية'),
    ], default='fr', string='Response Language')

    status = fields.Selection([
        ('not_loaded', 'Not Loaded'),
        ('loading',    'Chargement...'),
        ('ready',      'Prêt'),
        ('error',      'Erreur'),
    ], default='not_loaded', string='Statut', compute='_compute_status')

    system_prompt = fields.Text(
        string='Prompt système',
        default=(
            "You are an expert AI assistant for a company using Odoo ERP.\n"
            "Tu as accès en lecture seule à TOUTES les données de l'entreprise en temps réel.\n"
            "Tu réponds toujours de manière précise, professionnelle et concise.\n"
            "When presenting numerical data, structure your response clearly.\n"
            "Si une information n'est pas disponible, tu le signales clairement.\n"
            "Tu ne modifies JAMAIS les données : lecture seule uniquement."
        )
    )

    _gpt4all_instances = {}
    _lock = threading.Lock()


    def _db_flag_key(self):
        return f'im_odoo_ai_agent.model_loaded_{self.id}'

    def _set_db_flag(self, value: str):
        self.env['ir.config_parameter'].sudo().set_param(self._db_flag_key(), value)

    def _compute_status(self):
        for record in self:
            if record.backend == 'ollama':
                flag = record.env['ir.config_parameter'].sudo().get_param(
                    record._db_flag_key(), default='not_loaded'
                )
                record.status = flag if flag in ('ready', 'loading', 'error') else 'not_loaded'
            else:
                if not GPT4ALL_AVAILABLE:
                    record.status = 'error'
                elif record.id in AiAgentConfig._gpt4all_instances:
                    record.status = 'ready'
                else:
                    flag = record.env['ir.config_parameter'].sudo().get_param(
                        record._db_flag_key(), default='not_loaded'
                    )
                    record.status = flag if flag in ('ready', 'loading', 'error') else 'not_loaded'

    def is_model_loaded(self) -> bool:
        if self.backend == 'ollama':
            flag = self.env['ir.config_parameter'].sudo().get_param(
                self._db_flag_key(), 'not_loaded'
            )
            return flag == 'ready'
        return self.id in AiAgentConfig._gpt4all_instances


    def action_load_model(self):
        self.ensure_one()
        if self.backend == 'ollama':
            return self._action_connect_ollama()
        return self._action_load_gpt4all()

    def _action_connect_ollama(self):
        self._set_db_flag('loading')
        url = (self.ollama_url or OLLAMA_DEFAULT_URL).rstrip('/')
        try:
            r = requests.get(f"{url}/api/tags", timeout=5)
            r.raise_for_status()
            available_models = [m['name'] for m in r.json().get('models', [])]

            model_tag = self.ollama_model or 'llama3'
            if model_tag.endswith(":cloud"):
                found = True
            else:
                found = any(
                    m == model_tag or m.startswith(model_tag + ':')
                    for m in available_models
                )
            if not found:
                self._set_db_flag('error')
                liste = ', '.join(available_models) or '(aucun)'
                raise UserError(_(
                    f"Le modèle '{model_tag}' n'est pas disponible dans Ollama.\n"
                    f"Modèles disponibles : {liste}\n\n"
                    f"Téléchargez-le avec : ollama pull {model_tag}"
                ))

            self._set_db_flag('ready')
            _logger.info(f"[AI Agent] Ollama connecté – modèle '{model_tag}' disponible sur {url}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Ollama Connected'),
                    'message': _(f"Model '{model_tag}' ready at {url}"),
                    'type': 'success',
                }
            }
        except UserError:
            raise
        except requests.exceptions.ConnectionError:
            self._set_db_flag('error')
            raise UserError(_(
                f"Cannot reach the Ollama server at {url}.\n"
                "Vérifiez qu'Ollama est lancé : ollama serve"
            ))
        except Exception as e:
            self._set_db_flag('error')
            raise UserError(_(f"Erreur Ollama : {e}"))

    def _action_load_gpt4all(self):
        if not GPT4ALL_AVAILABLE:
            raise UserError(_("GPT4All n'est pas installé !\nInstallez-le avec: pip install gpt4all"))

        with AiAgentConfig._lock:
            if self.id in AiAgentConfig._gpt4all_instances:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Already Loaded'),
                        'message': _(f'Le modèle {self.model_name} est déjà en mémoire.'),
                        'type': 'info',
                    }
                }
            self._set_db_flag('loading')
            try:
                model = GPT4All(
                    model_name=self.model_name,
                    model_path=self.model_path if self.model_path else None,
                    device=self.device,
                    n_threads=self.n_threads,
                    verbose=False,
                )
                AiAgentConfig._gpt4all_instances[self.id] = model
                self._set_db_flag('ready')
                import os
            except Exception as e:
                self._set_db_flag('error')
                raise UserError(_(f"Error loading the model:\n{e}"))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Model Loaded'),
                'message': _(f'Model {self.model_name} is ready!'),
                'type': 'success',
            }
        }

    def action_unload_model(self):
        self.ensure_one()
        with AiAgentConfig._lock:
            AiAgentConfig._gpt4all_instances.pop(self.id, None)
            self._set_db_flag('not_loaded')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Disconnected'),
                'message': _('The AI backend has been unloaded.'),
                'type': 'info',
            }
        }


    def generate_raw(self, full_prompt: str) -> str:
        self.ensure_one()
        if self.backend == 'ollama':
            return self._generate_ollama(full_prompt)
        if self.backend == 'openai':
            return self._generate_openai(full_prompt)
        if self.backend == 'anthropic':
            return self._generate_anthropic(full_prompt)
        if self.backend == 'gemini':
            return self._generate_gemini(full_prompt)
        if self.backend == 'openai_compat':
            return self._generate_openai(full_prompt, base_url=self.api_base_url)
        return self._generate_gpt4all(full_prompt)

    def _generate_openai(self, prompt: str, base_url: str = None) -> str:
        api_key = self.api_key
        if not api_key:
            return "[Erreur] Clé API OpenAI manquante. Configurez-la dans les paramètres de l'agent."

        url = (base_url or 'https://api.openai.com/v1').rstrip('/') + '/chat/completions'
        model = self.api_model or 'gpt-4o-mini'

        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data['choices'][0]['message']['content'].strip()
        except requests.exceptions.ConnectionError:
            _logger.error(f"[AI Agent] OpenAI/compat injoignable sur {url}")
            return "Cannot reach the OpenAI API. Please check your internet connection."
        except requests.exceptions.Timeout:
            _logger.error("[AI Agent] OpenAI timeout")
            return "The OpenAI API took too long to respond. Please try again."
        except Exception as e:
            _logger.error(f"[AI Agent] Erreur OpenAI generate: {e}")
            return f"Erreur lors de la génération OpenAI : {e}"

    def _generate_anthropic(self, prompt: str) -> str:
        api_key = self.api_key
        if not api_key:
            return "[Erreur] Clé API Anthropic manquante. Configurez-la dans les paramètres de l'agent."

        model = self.api_model or 'claude-haiku-4-5-20251001'
        url = 'https://api.anthropic.com/v1/messages'

        payload = {
            'model': model,
            'max_tokens': self.max_tokens,
            'messages': [{'role': 'user', 'content': prompt}],
        }
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json',
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data['content'][0]['text'].strip()
        except requests.exceptions.ConnectionError:
            _logger.error("[AI Agent] Anthropic API injoignable")
            return "Cannot reach the Anthropic API. Please check your internet connection."
        except requests.exceptions.Timeout:
            _logger.error("[AI Agent] Anthropic timeout")
            return "The Anthropic API took too long to respond. Please try again."
        except Exception as e:
            _logger.error(f"[AI Agent] Erreur Anthropic generate: {e}")
            return f"Erreur lors de la génération Anthropic : {e}"

    def _generate_gemini(self, prompt: str) -> str:
        api_key = self.api_key
        if not api_key:
            return "[Erreur] Clé API Google Gemini manquante. Configurez-la dans les paramètres de l'agent."

        model = self.api_model or 'gemini-2.0-flash'
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'

        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'maxOutputTokens': self.max_tokens,
                'temperature': self.temperature,
                'topP': self.top_p,
            },
        }
        try:
            r = requests.post(url, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        except requests.exceptions.ConnectionError:
            _logger.error("[AI Agent] Gemini API injoignable")
            return "Cannot reach the Gemini API. Please check your internet connection."
        except requests.exceptions.Timeout:
            _logger.error("[AI Agent] Gemini timeout")
            return "The Gemini API took too long to respond. Please try again."
        except Exception as e:
            _logger.error(f"[AI Agent] Erreur Gemini generate: {e}")
            return f"Erreur lors de la génération Gemini : {e}"

    def _generate_ollama(self, prompt: str) -> str:
        url        = (self.ollama_url or OLLAMA_DEFAULT_URL).rstrip('/')
        model_tag  = self.ollama_model or 'llama3'
        payload    = {
            'model':  model_tag,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': self.temperature,
                'top_p':       self.top_p,
                'num_predict': self.max_tokens,
            },
        }
        try:
            r = requests.post(
                f"{url}/api/generate",
                json=payload,
                timeout=300,
            )
            r.raise_for_status()
            data = r.json()
            return data.get('response', '').strip()
        except requests.exceptions.ConnectionError:
            _logger.error(f"[AI Agent] Ollama injoignable sur {url}")
            return (
                "Le serveur Ollama ne répond pas. "
                "Vérifiez qu'il est lancé (ollama serve) et que l'URL est correcte."
            )
        except requests.exceptions.Timeout:
            _logger.error("[AI Agent] Ollama timeout")
            return "The Ollama model took too long to respond. Please try again."
        except Exception as e:
            _logger.error(f"[AI Agent] Erreur Ollama generate: {e}")
            return f"Erreur lors de la génération Ollama : {e}"

    def action_test_api_connection(self):
        self.ensure_one()
        if self.backend not in ('openai', 'anthropic', 'gemini', 'openai_compat'):
            raise UserError(_("Ce bouton est réservé aux backends API externes (OpenAI, Anthropic, Gemini)."))

        if not self.api_key:
            raise UserError(_("Veuillez d'abord renseigner votre clé API."))

        test_prompt = "Réponds uniquement par 'OK' en un mot."
        try:
            result = self.generate_raw(test_prompt)
            if result and not result.startswith("[Erreur]"):
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connexion réussie ✓'),
                        'message': _(f"L'API répond correctement. Modèle : {self.api_model}\nRéponse : {result[:100]}"),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_(f"L'API a renvoyé une erreur :\n{result}"))
        except UserError:
            raise
        except Exception as e:
            raise UserError(_(f"Erreur de connexion :\n{e}"))

    def generate_streaming(self, prompt: str):
        self.ensure_one()
        if self.backend != 'ollama':
            yield self._generate_gpt4all(prompt)
            return

        url       = (self.ollama_url or OLLAMA_DEFAULT_URL).rstrip('/')
        model_tag = self.ollama_model or 'llama3'
        payload   = {
            'model':  model_tag,
            'prompt': prompt,
            'stream': True,
            'options': {
                'temperature': self.temperature,
                'top_p':       self.top_p,
                'num_predict': self.max_tokens,
            },
        }
        try:
            with requests.post(
                f"{url}/api/generate",
                json=payload,
                timeout=300,
                stream=True,
            ) as r:
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
            _logger.error(f"[AI Agent] Streaming Ollama error: {e}")
            yield f"\n[Erreur streaming : {e}]"

    def _generate_gpt4all(self, full_prompt: str) -> str:
        model = self._get_gpt4all_instance()

        try:
            n_ctx = (
                model.config.get('n_ctx')
                or getattr(model.model, 'context_length', None)
                or self.n_ctx
            )
        except Exception:
            n_ctx = self.n_ctx

        max_prompt_chars = int(n_ctx * 4 * 0.75)

        if len(full_prompt) > max_prompt_chars:
            excess  = len(full_prompt) - max_prompt_chars
            cut_pos = full_prompt.find('\n', excess)
            full_prompt = full_prompt[cut_pos if cut_pos != -1 else excess:]
            _logger.warning(f"[AI Agent] Prompt GPT4All tronqué à {max_prompt_chars} chars")

        try:
            response = model.generate(
                full_prompt,
                max_tokens=self.max_tokens,
                temp=self.temperature,
                top_p=self.top_p,
            )
            return response.strip()
        except Exception as e:
            _logger.error(f"[AI Agent] Erreur GPT4All generate: {e}")
            return f"Erreur de génération GPT4All : {e}"

    def _get_gpt4all_instance(self):
        self.ensure_one()
        if self.id in AiAgentConfig._gpt4all_instances:
            return AiAgentConfig._gpt4all_instances[self.id]

        flag = self.env['ir.config_parameter'].sudo().get_param(self._db_flag_key(), 'not_loaded')
        if flag == 'ready':
            _logger.info("[AI Agent] Rechargement GPT4All automatique dans ce worker")
            self._action_load_gpt4all()

        model = AiAgentConfig._gpt4all_instances.get(self.id)
        if not model:
            raise UserError(_(
                "Le modèle GPT4All n'est pas chargé dans ce worker.\n"
                "Cliquez sur 'Charger le modèle' dans la configuration."
            ))
        return model


    def generate_response(self, user_message: str, context_data: str = None) -> str:
        self.ensure_one()
        try:
            response, _ = self.env['ai.odoo.tool'].run_agent_loop(user_message, self)
            return response
        except Exception as e:
            _logger.error(f"[AI Agent] Erreur generate_response: {e}")
            prompt = self.system_prompt + "\n\n"
            if context_data:
                prompt += f"Données Odoo :\n{context_data}\n\n"
            prompt += f"Question: {user_message}\n\nRéponse:"
            return self.generate_raw(prompt)

    @api.model
    def get_active_config(self):
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            config = self.create({'name': 'Agent IA Principal'})
        return config

    @api.model
    def get_status_for_controller(self) -> dict:
        config = self.get_active_config()
        backend = config.backend or 'gpt4all'

        if backend == 'ollama':
            backend_available = True
            model_label = f"Ollama – {config.ollama_model or 'llama3'}"
        else:
            backend_available = GPT4ALL_AVAILABLE
            model_label = config.model_name or ''

        return {
            'backend':           backend,
            'gpt4all_available': GPT4ALL_AVAILABLE,
            'backend_available': backend_available,
            'model_name':        model_label,
            'model_loaded':      config.is_model_loaded(),
            'config_id':         config.id,
            'status':            config.status,
            'ollama_url':        config.ollama_url if backend == 'ollama' else None,
        }

    @api.model
    def list_ollama_models(self) -> list:
        config = self.get_active_config()
        url = (config.ollama_url or OLLAMA_DEFAULT_URL).rstrip('/')
        try:
            r = requests.get(f"{url}/api/tags", timeout=5)
            r.raise_for_status()
            return [m['name'] for m in r.json().get('models', [])]
        except Exception as e:
            _logger.warning(f"[AI Agent] list_ollama_models error: {e}")
            return []