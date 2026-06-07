
import logging
import time
from odoo import models, fields, api, _
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class AiChatSession(models.Model):
    _name        = 'ai.chat.session'
    _description = 'Session de conversation IA'
    _order       = 'write_date desc'
    _rec_name    = 'title'

    title     = fields.Char(string='Title', default='New Conversation')
    user_id   = fields.Many2one('res.users', string='User', default=lambda s: s.env.uid, readonly=True)
    is_pinned = fields.Boolean(string='Pinned', default=False)
    active    = fields.Boolean(default=True)

    message_ids   = fields.One2many('ai.chat.message', 'session_id', string='Messages')
    message_count = fields.Integer(compute='_compute_message_count', store=True)

    config_id = fields.Many2one(
        'ai.agent.config',
        string='Config IA',
        compute='_compute_config_id',
    )

    @api.depends('message_ids')
    def _compute_message_count(self):
        for session in self:
            session.message_count = len(session.message_ids)

    def _compute_config_id(self):
        config = self.env['ai.agent.config'].get_active_config()
        for session in self:
            session.config_id = config

    def _get_or_create_session(self, session_id=None):
        if session_id:
            session = self.browse(int(session_id))
            if session.exists() and session.user_id.id == self.env.uid:
                return session
        return self.create({'title': 'New Conversation', 'user_id': self.env.uid})

    def send_message(self, user_message: str) -> dict:
        self.ensure_one()
        start_time = time.time()

        config = self.env['ai.agent.config'].get_active_config()
        if not config:
            return {'error': "Aucune configuration IA active trouvée."}

        self.env['ai.chat.message'].create({
            'session_id': self.id,
            'role':       'user',
            'content':    user_message,
        })

        count_after = self.env['ai.chat.message'].search_count(
            [('session_id', '=', self.id)]
        )
        if count_after == 1:
            title = user_message[:60] + ('…' if len(user_message) > 60 else '')
            self.write({'title': title})

        try:
            odoo_tool = self.env['ai.odoo.tool']
            response_text, sources = odoo_tool.run_agent_loop(
                user_question=user_message,
                config=config,
                session=self,
            )
        except Exception as e:
            _logger.error(f"[AI Agent] send_message error: {e}", exc_info=True)
            response_text = f"Une erreur s'est produite lors du traitement : {e}"
            sources       = ""

        elapsed = round(time.time() - start_time, 2)

        self.env['ai.chat.message'].create({
            'session_id':   self.id,
            'role':         'assistant',
            'content':      response_text,
            'sources':      sources or False,
            'response_time': elapsed,
        })

        return {
            'success':       True,
            'content':       response_text,
            'sources':       sources,
            'response_time': elapsed,
        }

    def get_messages_for_api(self) -> list:
        self.ensure_one()
        messages = []
        for msg in self.message_ids.sorted('create_date'):
            messages.append({
                'id':            msg.id,
                'role':          msg.role,
                'content':       msg.content or '',
                'create_date':   msg.create_date.isoformat() if msg.create_date else '',
                'is_error':      msg.is_error,
                'is_typing':     False,
                'response_time': msg.response_time,
            })
        return messages

    def action_clear_history(self):
        self.ensure_one()
        self.message_ids.unlink()
        self.write({'title': 'New Conversation'})


class AiChatMessage(models.Model):
    _name        = 'ai.chat.message'
    _description = 'Message de conversation IA'
    _order       = 'create_date asc'

    session_id    = fields.Many2one('ai.chat.session', required=True, ondelete='cascade', index=True)
    role          = fields.Selection([('user', 'Utilisateur'), ('assistant', 'Assistant')], required=True)
    content       = fields.Text(string='Contenu')
    is_error      = fields.Boolean(default=False)
    sources       = fields.Text(string='Sources consultées')
    response_time = fields.Float(string='Temps de réponse (s)')
    tokens_used   = fields.Integer(string='Tokens utilisés', default=0)
