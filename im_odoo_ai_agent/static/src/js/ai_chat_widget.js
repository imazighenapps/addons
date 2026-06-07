


import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { markup } from "@odoo/owl";


function sanitizeMessages(messages) {
    if (!Array.isArray(messages)) return [];
    return messages
        .filter(
            m =>
                m &&
                typeof m === 'object' &&
                typeof m.role === 'string' &&
                m.content !== undefined &&
                m.role !== 'system'
        )
        .map(m => ({
            id:           m.id,
            role:         m.role,
            content:      String(m.content ?? ''),
            create_date:  m.create_date || '',
            is_error:     Boolean(m.is_error),
            is_typing:    Boolean(m.is_typing),
            is_streaming: Boolean(m.is_streaming),
            is_thinking:  Boolean(m.is_thinking),
            steps:        Array.isArray(m.steps) ? m.steps : [],
            currentStep:  m.currentStep || '',
            response_time: m.response_time || 0,
        }));
}


let _chartCounter = 0;


const _pendingCharts = [];


function renderPendingCharts() {

    setTimeout(() => {
        while (_pendingCharts.length > 0) {
            const { canvasId, chartDef } = _pendingCharts.shift();
            const canvas = document.getElementById(canvasId);
            if (!canvas) continue;
            try {

                if (typeof Chart === 'undefined') {
                    const script = document.createElement('script');
                    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js';
                    script.onload = () => _drawChart(canvas, chartDef);
                    document.head.appendChild(script);
                } else {
                    _drawChart(canvas, chartDef);
                }
            } catch(e) {
                canvas.parentElement.innerHTML =
                    `<div class="ai-chart-error">⚠️ Erreur graphique : ${e.message}</div>`;
            }
        }
    }, 80);
}

function _drawChart(canvas, def) {
    const PALETTE = [
        '#6366f1','#8b5cf6','#06b6d4','#10b981',
        '#f59e0b','#ef4444','#3b82f6','#ec4899',
    ];
    new Chart(canvas, {
        type: def.type || 'bar',
        data: {
            labels: def.labels || [],
            datasets: [{
                label: def.title || '',
                data: def.data || [],
                backgroundColor: (def.type === 'line')
                    ? 'rgba(99,102,241,0.12)'
                    : def.data.map((_, i) => PALETTE[i % PALETTE.length]),
                borderColor: (def.type === 'line')
                    ? '#6366f1'
                    : def.data.map((_, i) => PALETTE[i % PALETTE.length]),
                borderWidth: def.type === 'line' ? 2 : 0,
                tension: 0.3,
                fill: def.type === 'line',
                borderRadius: def.type === 'bar' ? 6 : 0,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: !!def.title,
                    text: def.title || '',
                    font: { size: 13, weight: '600' },
                    color: '#374151',
                    padding: { bottom: 12 },
                },
            },
            scales: def.type === 'pie' || def.type === 'doughnut' ? {} : {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11 }, color: '#6b7280' },
                },
                y: {
                    grid: { color: '#f3f4f6' },
                    ticks: { font: { size: 11 }, color: '#6b7280' },
                    beginAtZero: true,
                },
            },
        },
    });
}


function parseChartBlock(raw) {
    try {
        const parts = raw.trim().split(':');
        const chartType = parts[1] ? parts[1].trim() : 'bar';
        const jsonPart  = raw.substring(raw.indexOf('{'));
        const def       = JSON.parse(jsonPart);
        def.type = chartType;
        return def;
    } catch { return null; }
}


function renderMarkdownTable(tableText) {
    const rows = tableText.trim().split('\n').filter(r => r.trim());
    if (rows.length < 2) return tableText;

    const parseRow = row =>
        row.split('|').map(c => c.trim()).filter((_, i, a) => i > 0 && i < a.length - 1);

    const headers  = parseRow(rows[0]);
    const dataRows = rows.slice(2);

    const ths = headers.map(h =>
        `<th>${h.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</th>`
    ).join('');

    const trs = dataRows.map(r =>
        `<tr>${parseRow(r).map(c =>
            `<td>${c.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</td>`
        ).join('')}</tr>`
    ).join('');

    return `<div class="ai-table-wrap"><table class="ai-table"><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table></div>`;
}

function markdownToHtml(text) {
    if (!text) return '';


    const blocks = [];
    const placeholder = (html) => {
        const idx = blocks.length;
        blocks.push(html);
        return `\x00BLOCK${idx}\x00`;
    };


    text = text.replace(/```chart\n?([\s\S]*?)```/gi, (_, inner) => {
        const def = parseChartBlock('CHART:bar:' + inner.trim().replace(/^CHART:[a-z]+:/i,''));

        const typeMatch = inner.trim().match(/^([a-z]+)[\s\n]/i);
        if (def && typeMatch) def.type = typeMatch[1].toLowerCase();
        if (!def) return placeholder(`<div class="ai-chart-error">⚠️ Données graphique invalides</div>`);
        const id = `ai-chart-${++_chartCounter}`;
        _pendingCharts.push({ canvasId: id, chartDef: def });
        return placeholder(`<div class="ai-chart-wrap"><canvas id="${id}"></canvas></div>`);
    });


    text = text.replace(/^CHART:([a-z]+):(.*)/gmi, (match) => {
        const def = parseChartBlock(match);
        if (!def) return match;
        const id = `ai-chart-${++_chartCounter}`;
        _pendingCharts.push({ canvasId: id, chartDef: def });
        return placeholder(`<div class="ai-chart-wrap"><canvas id="${id}"></canvas></div>`);
    });


    text = text.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
        const escaped = code
            .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        const langLabel = lang ? `<span class="ai-code-lang">${lang}</span>` : '';
        return placeholder(
            `<div class="ai-code-block">${langLabel}<pre><code>${escaped.trim()}</code></pre></div>`
        );
    });


    text = text.replace(/((\|[^\n]+\|\n?)+)/g, (match) => {
        if (!match.includes('|')) return match;
        const lines = match.trim().split('\n');

        const hasSep = lines.some(l => /^\|[\s\-|:]+\|$/.test(l.trim()));
        if (!hasSep || lines.length < 2) return match;
        return placeholder(renderMarkdownTable(match));
    });


    text = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');


    text = text

        .replace(/^### (.+)$/gm, '<h4 class="ai-h4">$1</h4>')
        .replace(/^## (.+)$/gm,  '<h3 class="ai-h3">$1</h3>')
        .replace(/^# (.+)$/gm,   '<h2 class="ai-h2">$1</h2>')

        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g,     '<em>$1</em>')

        .replace(/`([^`]+)`/g, '<code class="ai-code-inline">$1</code>')

        .replace(/^[\s]*[•·\-\*]\s(.+)$/gm, '<li>$1</li>')
        .replace(/^[\s]*(\d+)\.\s(.+)$/gm,  '<li class="ai-li-num">$2</li>')

        .replace(/^---+$/gm, '<hr class="ai-hr">')

        .replace(/\n/g, '<br>');


    text = text.replace(/(<li(?:[^>]*)>[\s\S]*?<\/li>)(\s*<br>\s*(<li(?:[^>]*)>[\s\S]*?<\/li>))*/g,
        match => `<ul class="ai-ul">${match.replace(/<br>/g,'')}</ul>`
    );


    text = text.replace(/\x00BLOCK(\d+)\x00/g, (_, i) => blocks[parseInt(i)]);

    return text;
}


class ChatMessage extends Component {
    static template = "ai_agent.ChatMessage";

    static props = {
        message: {
            type: Object,
            shape: {
                id:           { type: [Number, String] },
                role:         String,
                content:      String,
                create_date:  { type: String,  optional: true },
                is_error:     { type: Boolean, optional: true },
                is_typing:    { type: Boolean, optional: true },
                is_streaming: { type: Boolean, optional: true },
                is_thinking:  { type: Boolean, optional: true },
                steps:        { type: Array,   optional: true },
                currentStep:  { type: String,  optional: true },
                response_time:{ type: Number,  optional: true },
            },
        },
    };

    get formattedTime() {
        const d = this.props.message.create_date;
        if (!d) return '';
        try {
            return new Date(d).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        } catch {
            return '';
        }
    }


   get formattedContent() {
        const html = markdownToHtml(this.props.message.content || '');
        if (_pendingCharts.length > 0) {
            renderPendingCharts();
        }
        return markup(html);
    }

    get responseTimeLabel() {
        const t = this.props.message.response_time;
        return t && t > 0 ? `⚡ ${t}s` : '';
    }
}


class AiChatInterface extends Component {
    static template = "ai_agent.ChatInterface";
    static components = { ChatMessage };

    setup() {
        this.notification = useService("notification");

        this.state = useState({
            sessions: [],
            currentSessionId: null,
            showSidebar: true,

            messages: [],
            isLoading: false,
            isTyping: false,

            inputText: '',

            modelStatus: 'checking',
            modelName:   '',
            backend:     'gpt4all',

            suggestions: [],
            showSuggestions: true,

            lastResponseTime: 0,
        });

        this.messagesEndRef = useRef('messagesEnd');
        this.inputRef = useRef('chatInput');

        onMounted(async () => {
            await this._checkModelStatus();
            await this._loadSessions();
            if (!this.state.currentSessionId) {
                await this._createNewSession();
            }
        });
    }


    async _checkModelStatus() {
        try {
            const result = await rpc('/ai_agent/config/status', {});
            if (result.error) { this.state.modelStatus = 'error'; return; }
            this.state.modelName  = result.model_name || '';
            this.state.backend    = result.backend    || 'gpt4all';
            this.state.suggestions = Array.isArray(result.suggestions) ? result.suggestions : [];

            if (this.state.backend === 'ollama') {

                this.state.modelStatus = result.model_loaded ? 'ready' : 'not_loaded';
            } else {

                if (!result.gpt4all_available) {
                    this.state.modelStatus = 'not_installed';
                } else {
                    this.state.modelStatus = result.model_loaded ? 'ready' : 'not_loaded';
                }
            }
        } catch {
            this.state.modelStatus = 'error';
        }
    }

    async _loadModel() {
        this.state.modelStatus = 'loading';
        try {

            const result = await rpc('/ai_agent/config/load_model', {});
            if (result.success) {
                this.state.modelStatus = 'ready';
                this.notification.add('AI model loaded successfully!', { type: 'success' });
            } else {
                this.state.modelStatus = 'error';
                this.notification.add(result.error || 'Loading error', { type: 'danger' });
            }
        } catch (e) {
            this.state.modelStatus = 'error';
            this.notification.add('Unable to load the model', { type: 'danger' });
        }
    }


    async _loadSessions() {
        try {
            const result = await rpc('/ai_agent/session/list', {});
            if (result.sessions) {
                this.state.sessions = result.sessions;
                if (result.sessions.length > 0 && !this.state.currentSessionId) {
                    await this._selectSession(result.sessions[0].id);
                }
            }
        } catch (e) {
            console.error('Error loading sessions:', e);
        }
    }

    async _createNewSession() {
        try {

            const result = await rpc('/ai_agent/session/create', {});
            if (result.session_id) {
                this.state.currentSessionId = result.session_id;
                this.state.messages = [];
                this.state.showSuggestions = true;
                await this._loadSessions();
            }
        } catch (e) {
            console.error('Error creating session:', e);
        }
    }

    async _selectSession(sessionId) {
        this.state.currentSessionId = sessionId;
        this.state.showSuggestions = false;
        try {
            const result = await rpc('/ai_agent/session/messages', { session_id: sessionId });
            this.state.messages = sanitizeMessages(result.messages);
            if (this.state.messages.length === 0) {
                this.state.showSuggestions = true;
            }
            this._scrollToBottom();
        } catch {
            this.state.messages = [];
        }
    }

    async _deleteSession(sessionId, event) {
        event.stopPropagation();
        try {
            const result = await rpc('/ai_agent/session/delete', { session_id: sessionId });
            if (result.success) {
                if (this.state.currentSessionId === sessionId) {
                    this.state.currentSessionId = null;
                    this.state.messages = [];
                    await this._createNewSession();
                }
                await this._loadSessions();
            }
        } catch (e) {
            console.error('Error deleting session:', e);
        }
    }


    async sendMessage(text = null) {
        const message = (text || this.state.inputText).trim();
        if (!message || this.state.isLoading) return;

        if (!this.state.currentSessionId) {
            await this._createNewSession();
        }

        this.state.inputText     = '';
        this.state.showSuggestions = false;
        this.state.isLoading     = true;
        this.state.isTyping      = true;


        const userMsgId = `tmp_${Date.now()}`;
        const assistantMsgId = `stream_${Date.now()}`;

        this.state.messages = sanitizeMessages([
            ...this.state.messages,
            {
                id: userMsgId, role: 'user', content: message,
                create_date: new Date().toISOString(),
                is_error: false, is_typing: false, response_time: 0,
            },
            {
                id: assistantMsgId, role: 'assistant', content: '',
                create_date: '', is_error: false, is_typing: false,
                response_time: 0, steps: [], is_streaming: true,
            },
        ]);
        this._scrollToBottom();

        const url = `/ai_agent/chat/stream?session_id=${this.state.currentSessionId}&message=${encodeURIComponent(message)}`;
        const evtSource = new EventSource(url);
        let accumulatedContent = '';
        let thinkingBuffer = '';
        let isThinking = false;

        const updateStreamMsg = (patch) => {
            this.state.messages = this.state.messages.map(m =>
                m.id === assistantMsgId ? { ...m, ...patch } : m
            );
            this._scrollToBottom();
        };

        evtSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'step') {

                    updateStreamMsg({ currentStep: data.content, steps: [data.content] });
                }
                else if (data.type === 'thinking_start') {
                    isThinking = true;
                    thinkingBuffer = '';
                    updateStreamMsg({ is_thinking: true });
                }
                else if (data.type === 'thinking_end') {
                    isThinking = false;
                    updateStreamMsg({ is_thinking: false });
                }
                else if (data.type === 'token') {
                    if (!isThinking) {
                        accumulatedContent += data.content;
                        updateStreamMsg({ content: accumulatedContent, is_typing: false });
                    }
                }
                else if (data.type === 'done') {
                    evtSource.close();
                    updateStreamMsg({
                        content: accumulatedContent,
                        is_streaming: false,
                        is_typing: false,
                        is_thinking: false,
                        steps: [],
                        currentStep: '',
                    });
                    this.state.isLoading = false;
                    this.state.isTyping  = false;
                    this._loadSessions();
                    this._focusInput();
                }
                else if (data.type === 'error') {
                    evtSource.close();
                    updateStreamMsg({
                        content: `⚠️ ${data.content}`,
                        is_error: true,
                        is_streaming: false,
                        is_typing: false,
                    });
                    this.state.isLoading = false;
                    this.state.isTyping  = false;
                    this._focusInput();
                }
            } catch(e) {
                console.error('SSE parse error:', e);
            }
        };

        evtSource.onerror = () => {
            evtSource.close();
            if (this.state.isLoading) {
                updateStreamMsg({
                    content: accumulatedContent || '⚠️ Connection interrupted.',
                    is_error: !accumulatedContent,
                    is_streaming: false,
                    is_typing: false,
                });
                this.state.isLoading = false;
                this.state.isTyping  = false;
                this._focusInput();
            }
        };
    }


    onInputKeydown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }

    onInputChange(event) {
        this.state.inputText = event.target.value;
        const ta = event.target;
        ta.style.height = 'auto';
        ta.style.height = Math.min(ta.scrollHeight, 150) + 'px';
    }

    onSuggestionClick(suggestion) { this.sendMessage(suggestion); }
    onNewChat()                    { this._createNewSession(); }
    onSessionClick(sessionId)      { this._selectSession(sessionId); }
    onDeleteSession(sessionId, ev) { this._deleteSession(sessionId, ev); }
    toggleSidebar()                { this.state.showSidebar = !this.state.showSidebar; }


    _scrollToBottom() {
        setTimeout(() => {
            if (this.messagesEndRef.el) {
                this.messagesEndRef.el.scrollIntoView({ behavior: 'smooth' });
            }
        }, 50);
    }

    _focusInput() {
        setTimeout(() => {
            if (this.inputRef.el) this.inputRef.el.focus();
        }, 100);
    }

    get currentSession() {
        return this.state.sessions.find(s => s.id === this.state.currentSessionId);
    }

    get statusLabel() {
        const isOllama = this.state.backend === 'ollama';
        const labels = {
            checking:      '⏳ Vérification...',
            ready:         isOllama ? '🟢 Ollama connected' : '🟢 Model ready',
            not_loaded:    isOllama ? '🟡 Ollama not connected' : '🟡 Model not loaded',
            loading:       isOllama ? '⏳ Connecting...' : '⏳ Loading...',
            error:         '🔴 Error',
            not_installed: '⚠️ GPT4All not installed',
        };
        return labels[this.state.modelStatus] || '❓ Inconnu';
    }

    get canSend() {
        return !this.state.isLoading && this.state.inputText.trim().length > 0;
    }
}


registry.category("actions").add("ai_agent.ChatInterface", AiChatInterface);
export { AiChatInterface, ChatMessage };