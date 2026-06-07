
{
    'name': 'AI Agent Assistant',
    'version': '18.0.3.1.0',
    'category': 'Productivity',
    'summary': 'Local AI assistant for managers and employees (GPT4All, Ollama, OpenAI, Claude, Gemini)',
    'description': """
        AI Agent Module for Odoo 18
        ===========================
        Ask questions in natural language and get answers
        based on your real-time Odoo data.

        Features:
        - Interactive natural language chat with session memory
        - Automatic and dynamic queries on Odoo data
        - Local AI via GPT4All (no data sent externally)
        - Optimized ReAct loop with intent classifier
        - Dynamic suggestions based on installed modules
        - Conversation history with pinning
        - Data access audit log
        - Odoo multi-worker compatible (DB-level loading flag)
        - Cloud API support: OpenAI (ChatGPT), Anthropic (Claude), Google Gemini
        - OpenAI-compatible API support: Mistral, Groq, Together AI...
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'price': 34.99,
    'currency': 'EUR',

    'depends': [
        'base',
        'mail',
        'web',
    ],

    'depends_optional': [
        'account',
        'sale',
        'purchase',
        'stock',
        'hr',
        'project',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/ai_agent_views.xml',
        'views/ai_chat_session_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
        'data/ai_agent_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'im_odoo_ai_agent/static/src/css/ai_chat.css',
            'im_odoo_ai_agent/static/src/xml/ai_chat_widget.xml',
            'im_odoo_ai_agent/static/src/js/ai_chat_widget.js',
            'im_odoo_ai_agent/static/src/js/ai_agent_action.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],    
}
