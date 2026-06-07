

import logging
import json
import re
from datetime import date, datetime
from odoo import models, api, _

_logger = logging.getLogger(__name__)

EXCLUDED_MODEL_PREFIXES = (
    'ir.rule', 'ir.model.access', 'base.setup',
    'mail.message', 'mail.tracking', 'mail.channel',
    'bus.', 'report.', 'web.',
)

MAX_RECORDS       = 50
MAX_ITERATIONS    = 6
MAX_HISTORY_TURNS = 4

_ALL_PRIORITY_FIELDS = {
    'account.move': [
        'name', 'move_type', 'state', 'partner_id', 'invoice_date',
        'invoice_date_due', 'amount_total', 'amount_residual', 'currency_id',
        'journal_id', 'payment_state',
    ],
    'sale.order': [
        'name', 'state', 'partner_id', 'date_order', 'amount_total',
        'amount_untaxed', 'currency_id', 'user_id', 'team_id',
    ],
    'sale.order.line': [
        'order_id', 'product_id', 'product_uom_qty', 'price_unit',
        'price_subtotal', 'qty_delivered', 'qty_invoiced',
    ],
    'purchase.order': [
        'name', 'state', 'partner_id', 'date_order', 'amount_total',
        'currency_id', 'user_id',
    ],
    'res.partner': [
        'name', 'is_company', 'customer_rank', 'supplier_rank', 'email',
        'phone', 'city', 'country_id', 'vat',
    ],
    'product.template': [
        'name', 'type', 'categ_id', 'list_price', 'standard_price',
        'active', 'sale_ok', 'purchase_ok', 'uom_id',
    ],
    'product.product': [
        'name', 'product_tmpl_id', 'default_code', 'barcode',
        'lst_price', 'standard_price', 'qty_available',
    ],
    'hr.employee': [
        'name', 'job_title', 'job_id', 'department_id', 'company_id',
        'active', 'employee_type', 'work_email',
    ],
    'stock.quant': [
        'product_id', 'location_id', 'quantity', 'reserved_quantity',
        'lot_id', 'package_id',
    ],
    'stock.picking': [
        'name', 'picking_type_id', 'partner_id', 'state', 'scheduled_date',
        'date_done', 'origin',
    ],
    'project.project': [
        'name', 'partner_id', 'user_id', 'date_start', 'date',
        'last_update_status', 'tag_ids',
    ],
    'project.task': [
        'name', 'project_id', 'user_ids', 'stage_id', 'date_deadline',
        'priority', 'state', 'tag_ids',
    ],
}

_ALL_INTENT_MODEL_MAP = [
    (r'\b(facture|invoice|bill|avoir|credit.?note|comptabilit|paiement|payment|encaissement|d[eé]bit|cr[eé]dit|tax|tva|bilan|journal)\b',
     ['account.move', 'account.payment']),
    (r'\b(vente|sale|commande.client|bon.de.commande|devis|quotation|chiffre.d\'affaires|ca\b|revenue|ligne.de.commande|order.line)\b',
     ['sale.order', 'sale.order.line']),
    (r'\b(achat|purchase|commande.achat|fournisseur|supplier|approvisionnement)\b',
     ['purchase.order', 'purchase.order.line']),
    (r'\b(client|customer|partner|contact|prospect|fidélit[eé])\b',
     ['res.partner']),
    (r'\b(produit|product|article|catalogue|prix|price|tarif)\b',
     ['product.template', 'product.product']),
    (r'\b(employ[eé]|employee|personnel|staff|rh|hr|salaire|salary|cong[eé]|leave|contrat|contract)\b',
     ['hr.employee']),
    (r'\b(stock|inventaire|inventory|entrep[oô]t|warehouse|quantit[eé]|qty|livraison|delivery|r[eé]ception)\b',
     ['stock.quant', 'stock.picking']),
    (r'\b(projet|project|t[aâ]che|task|jalon|milestone|étape)\b',
     ['project.project', 'project.task']),
]

PRIORITY_FIELDS  = _ALL_PRIORITY_FIELDS
INTENT_MODEL_MAP = _ALL_INTENT_MODEL_MAP

CHITCHAT_PATTERNS = [
    r'^(bonjour|bonsoir|salut|coucou|hello|hi|hey|salam|مرحبا|good\s*(morning|afternoon|evening))[^a-z]*$',
    r'^(merci|thanks|thank you|شكرا)[^a-z]*$',
    r'^(ok|oui|non|yes|no|d\'accord|okay|parfait|super|bien|ça marche|génial)[^a-z]*$',
    r'^(comment (tu|vous) (vas|allez|t\'appelles?|vous appelez))[^a-z]*$',
    r'^(qui es.?tu|what are you|tu es quoi|tu fais quoi)[^a-z]*$',
    r'^(aide|help|aide.?moi|que (peux.?tu|sais.?tu) faire)[^a-z]*$',
]

AGGREGATE_PATTERNS = [
    r'\b(total|somme|sum|montant.total|chiffre.d\'affaires|ca\b|statistique|stat|combien|count|nombre|top\s*\d|meilleur|premier|classement|ranking|moyenne|average|r[eé]sum[eé])\b',
]

LANG_LABELS = {
    'fr': 'Always respond in French.',
    'en': 'Always respond in English.',
    'ar': 'أجب دائماً باللغة العربية.',
}


class AiOdooTool(models.AbstractModel):
    _name        = 'ai.odoo.tool'
    _description = "Dynamic Odoo Data Access Engine for AI Agent (Read-Only) v4"


    @api.model
    def _get_active_intent_map(self) -> list:
        active_map = []
        for pattern, model_list in _ALL_INTENT_MODEL_MAP:
            available = [m for m in model_list if m in self.env]
            if available:
                active_map.append((pattern, available))
        return active_map

    @api.model
    def _get_active_priority_fields(self) -> dict:
        return {
            model: fields
            for model, fields in _ALL_PRIORITY_FIELDS.items()
            if model in self.env
        }

    @api.model
    def _classify_question(self, question: str) -> dict:
        q = question.lower().strip()

        for pat in CHITCHAT_PATTERNS:
            if re.search(pat, q, re.IGNORECASE):
                return {"is_chitchat": True, "candidate_models": [], "needs_aggregate": False}

        candidate_models = []
        for pattern, model_list in self._get_active_intent_map():
            if re.search(pattern, q, re.IGNORECASE):
                for m in model_list:
                    if m not in candidate_models:
                        candidate_models.append(m)

        needs_aggregate = any(
            re.search(p, q, re.IGNORECASE) for p in AGGREGATE_PATTERNS
        )

        return {
            "is_chitchat":       False,
            "candidate_models":  candidate_models,
            "needs_aggregate":   needs_aggregate,
        }


    @api.model
    def _get_schema_for_models(self, model_names: list) -> str:
        if not model_names:
            return "(no model specified)"

        lines = []
        for model_name in model_names:
            if model_name not in self.env:
                continue
            try:
                fields_info = self.env[model_name].fields_get(
                    attributes=['string', 'type', 'relation']
                )
                relevant = []
                for fname, fdata in fields_info.items():
                    if fname.startswith('_') or fname.startswith('message_'):
                        continue
                    ftype = fdata.get('type', '')
                    if ftype == 'one2many':
                        continue
                    entry = f"{fname}:{ftype}"
                    if ftype in ('many2one', 'many2many') and fdata.get('relation'):
                        entry += f"→{fdata['relation']}"
                    relevant.append(entry)

                model_obj = self.env['ir.model'].search(
                    [('model', '=', model_name)], limit=1
                )
                model_label = model_obj.name if model_obj else model_name
                lines.append(f"MODEL: {model_name} | {model_label}")
                lines.append(f"  FIELDS: {', '.join(relevant[:30])}")
            except Exception:
                continue

        return "\n".join(lines) if lines else "(models not accessible)"

    @api.model
    def _get_models_list(self) -> str:
        try:
            ir_models = self.env['ir.model'].search(
                [('transient', '=', False)], order='model asc', limit=400)
            lines = []
            for m in ir_models:
                if any(m.model.startswith(p) for p in EXCLUDED_MODEL_PREFIXES):
                    continue
                if m.model not in self.env:
                    continue
                lines.append(f"{m.model} | {m.name}")
            return "\n".join(lines)
        except Exception as e:
            _logger.error(f"_get_models_list error: {e}")
            return "sale.order | Commandes clients\npurchase.order | Commandes achats\nres.partner | Contacts\nproduct.template | Produits"

    def _get_candidate_schema(self, candidate_models: list) -> str:
        return self._get_models_list()

    @api.model
    def _get_odoo_schema(self, max_models: int = 120) -> str:
        try:
            ir_models = self.env['ir.model'].search(
                [('transient', '=', False)],
                order='model asc',
                limit=max_models * 2,
            )
            lines, count = [], 0
            for m in ir_models:
                if count >= max_models:
                    break
                if any(m.model.startswith(p) for p in EXCLUDED_MODEL_PREFIXES):
                    continue
                if m.model not in self.env:
                    continue
                try:
                    fields_info = self.env[m.model].fields_get(attributes=['string', 'type'])
                    relevant = [
                        f"{fn} ({fd['type']})"
                        for fn, fd in fields_info.items()
                        if fd['type'] not in ('one2many',) and not fn.startswith('__')
                    ][:12]
                    lines.append(f"{m.model} | {m.name} | {', '.join(relevant)}")
                    count += 1
                except Exception:
                    continue
            return "\n".join(lines)
        except Exception as e:
            _logger.error(f"_get_odoo_schema error: {e}")
            return "Erreur lors de la récupération du schéma Odoo."


    @api.model
    def _planning_step(self, question: str, candidate_schema: str, config, candidate_models: list = None) -> dict:
        models_list = self._get_models_list()

        prompt1 = f"""Tu es un expert Odoo ERP. Quelle(s) table(s) de données faut-il interroger pour répondre à cette question ?

QUESTION : {question}

TABLES DISPONIBLES :
{models_list}

Réponds UNIQUEMENT avec un JSON valide, sans texte, sans markdown :
{{"models": ["modele1", "modele2"]}}

Maximum 3 modèles. Choisis les plus pertinents pour la question."""

        try:
            raw1 = config.generate_raw(prompt1)
            m1 = re.search(r'\{[\s\S]*?\}', raw1)
            if not m1:
                _logger.warning("[AI Agent v4] Planning step 1: pas de JSON")
                return {"success": False}
            plan1 = json.loads(m1.group(0))
            chosen_models = [m for m in plan1.get("models", []) if m in self.env]
            if not chosen_models:
                _logger.warning(f"[AI Agent v4] Planning step 1: modèles invalides: {plan1}")
                return {"success": False}
        except Exception as e:
            _logger.warning(f"[AI Agent v4] Planning step 1 error: {e}")
            return {"success": False}

        detailed_schema = self._get_schema_for_models(chosen_models)

        prompt2 = f"""Tu es un expert Odoo ERP. Pour répondre à cette question, quels champs faut-il récupérer ?

QUESTION : {question}

SCHÉMA DES MODÈLES SÉLECTIONNÉS :
{detailed_schema}

Réponds UNIQUEMENT avec un JSON valide, sans texte, sans markdown :
{{
  "fields_map": {{
    "modele1": ["champ1", "champ2"],
    "modele2": ["champ1"]
  }},
  "strategy": "search",
  "order": "champ desc"
}}

strategy = "aggregate" si la question demande totaux/stats/count, sinon "search".
N'inclus QUE des champs présents dans le schéma fourni."""

        try:
            raw2 = config.generate_raw(prompt2)
            m2 = re.search(r'\{[\s\S]*\}', raw2)
            if not m2:
                _logger.warning("[AI Agent v4] Planning step 2: pas de JSON")
                return {"success": False}
            plan2 = json.loads(m2.group(0))
        except Exception as e:
            _logger.warning(f"[AI Agent v4] Planning step 2 error: {e}")
            return {"success": False}

        try:
            plan = plan2

            validated_fields_map = {}
            valid_models = []

            for model_name in plan.get('models', []):
                if model_name not in self.env:
                    _logger.warning(f"[AI Agent v4] Planning: modèle '{model_name}' inexistant, ignoré")
                    continue

                real_fields = set(self.env[model_name].fields_get().keys())
                requested   = plan.get('fields_map', {}).get(model_name, [])
                valid_fields = [f for f in requested if f in real_fields]

                if not valid_fields:
                    valid_fields = [
                        f for f in self._get_active_priority_fields().get(model_name, [])
                        if f in real_fields
                    ]

                if valid_fields:
                    validated_fields_map[model_name] = valid_fields
                    valid_models.append(model_name)

            if not valid_models:
                _logger.warning("[AI Agent v4] Planning step: aucun modèle valide après validation")
                return {"success": False}

            return {
                "success":    True,
                "models":     valid_models,
                "fields_map": validated_fields_map,
                "strategy":   plan.get('strategy', 'search'),
                "groupby":    plan.get('groupby', []),
                "order":      plan.get('order', None),
            }

        except (json.JSONDecodeError, KeyError) as e:
            _logger.warning(f"[AI Agent v4] Planning step JSON error: {e}")
            return {"success": False}
        except Exception as e:
            _logger.error(f"[AI Agent v4] Planning step error: {e}")
            return {"success": False}


    @api.model
    def get_dynamic_suggestions(self) -> list:
        suggestions = ["📊 Tableau de bord général de l'entreprise"]

        if 'account.move' in self.env:
            suggestions.append("📋 Factures à payer ce mois")
            suggestions.append("⚠️ Factures en retard de paiement")

        if 'sale.order' in self.env:
            suggestions.append("📈 Meilleures ventes de cette année")
            suggestions.append("🏆 Top 10 clients par chiffre d'affaires")
            suggestions.append("🥇 Top produits vendus ce trimestre")

        if 'purchase.order' in self.env:
            suggestions.append("🛒 Résumé des achats fournisseurs")

        if 'stock.quant' in self.env:
            suggestions.append("📦 Produits en rupture de stock")

        if 'hr.employee' in self.env:
            suggestions.append("👔 Résumé des ressources humaines")

        if 'project.task' in self.env:
            suggestions.append("📌 Tâches en retard sur les projets")

        return suggestions[:10]


    @api.model
    def execute_tool_call(self, tool_name: str, tool_args: dict) -> str:
        try:
            if tool_name == 'search_records':
                return self._tool_search_records(**tool_args)
            elif tool_name == 'get_model_fields':
                return self._tool_get_model_fields(**tool_args)
            elif tool_name == 'get_record_count':
                return self._tool_get_record_count(**tool_args)
            elif tool_name == 'aggregate_records':
                return self._tool_aggregate_records(**tool_args)
            else:
                return (
                    f"[ERREUR] Outil inconnu : '{tool_name}'. "
                    "Outils disponibles : search_records, aggregate_records, "
                    "get_record_count, get_model_fields."
                )
        except TypeError as e:
            return f"[ERREUR] Arguments invalides pour '{tool_name}': {e}"
        except Exception as e:
            _logger.error(f"execute_tool_call({tool_name}) error: {e}")
            return f"[ERREUR] {e}"

    @api.model
    def _tool_search_records(
        self,
        model: str,
        domain: list = None,
        fields: list = None,
        limit: int = 20,
        order: str = None,
    ) -> str:
        if model not in self.env:
            return f"[ERREUR] Modèle '{model}' introuvable."
        domain = domain or []
        fields = fields or []
        limit  = min(int(limit), MAX_RECORDS)

        model_fields = self.env[model].fields_get()
        stored_fields = {
            fname for fname, finfo in model_fields.items()
            if finfo.get('store', True) and not fname.startswith('_')
        }
        def _safe_field(f):
            if f == 'display_name':
                return 'name' if 'name' in model_fields else None
            return f if f in stored_fields else None

        safe_fields = [sf for f in fields for sf in [_safe_field(f)] if sf]
        if not safe_fields and 'name' in model_fields:
            safe_fields = ['name']

        clean_domain = []
        for leaf in domain:
            if isinstance(leaf, (list, tuple)) and len(leaf) == 3:
                fname = leaf[0]
                if fname == 'display_name':
                    fname = 'name'
                    leaf = [fname, leaf[1], leaf[2]]
                if fname in stored_fields:
                    clean_domain.append(leaf)
                else:
                    _logger.warning(f"[AI Agent] Champ non stocké ignoré dans domain: {fname}")
            else:
                clean_domain.append(leaf)

        try:
            records = self.env[model].search_read(
                domain=clean_domain,
                fields=safe_fields or None,
                limit=limit,
                order=order,
            )
            if not records:
                return f"[{model}] Aucun enregistrement trouvé pour ce domaine."

            lines = [f"[{model}] {len(records)} enregistrement(s) :"]
            for i, rec in enumerate(records, 1):
                cleaned = {}
                for k, v in rec.items():
                    if isinstance(v, tuple) and len(v) == 2:
                        cleaned[k] = v[1]
                    elif isinstance(v, (datetime, date)):
                        cleaned[k] = v.isoformat()
                    elif v is False:
                        cleaned[k] = None
                    else:
                        cleaned[k] = v
                lines.append(f"  {i}. {json.dumps(cleaned, ensure_ascii=False, default=str)}")
            return "\n".join(lines)
        except Exception as e:
            return f"[ERREUR search_records sur {model}]: {e}"

    @api.model
    def _tool_aggregate_records(
        self,
        model: str,
        domain: list = None,
        fields: list = None,
        groupby: list = None,
    ) -> str:
        if model not in self.env:
            return f"[ERREUR] Modèle '{model}' introuvable."
        domain  = domain or []
        fields  = fields or []
        groupby = groupby or []
        try:
            results = self.env[model].read_group(
                domain=domain,
                fields=fields,
                groupby=groupby,
                lazy=False,
            )
            if not results:
                return f"[{model}] Aucun résultat pour cette agrégation."

            lines = [f"[{model}] Résultat agrégé ({len(results)} groupe(s)) :"]
            for r in results[:30]:
                cleaned = {
                    k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v)
                    for k, v in r.items()
                    if not k.startswith('__')
                }
                lines.append(f"  {json.dumps(cleaned, ensure_ascii=False, default=str)}")
            return "\n".join(lines)
        except Exception as e:
            return f"[ERREUR aggregate_records sur {model}]: {e}"

    @api.model
    def _tool_get_model_fields(self, model: str, filter_type: str = None) -> str:
        if model not in self.env:
            return f"[ERREUR] Modèle '{model}' introuvable."
        try:
            fields_info = self.env[model].fields_get(attributes=['string', 'type', 'help'])
            lines = [f"Champs du modèle '{model}':"]
            for fname, fdata in fields_info.items():
                if fname.startswith('_'):
                    continue
                ftype = fdata.get('type', '')
                if filter_type and ftype != filter_type:
                    continue
                fstring  = fdata.get('string', fname)
                fhelp    = fdata.get('help', '')
                help_part = f" — {fhelp[:80]}" if fhelp else ""
                lines.append(f"  • {fname} ({ftype}) : {fstring}{help_part}")
            return "\n".join(lines)
        except Exception as e:
            return f"[ERREUR get_model_fields sur {model}]: {e}"

    @api.model
    def _tool_get_record_count(self, model: str, domain: list = None) -> str:
        if model not in self.env:
            return f"[ERREUR] Modèle '{model}' introuvable."
        domain = domain or []
        try:
            count  = self.env[model].search_count(domain)
            suffix = " (filtrés)" if domain else ""
            return f"[{model}] Nombre d'enregistrements{suffix} : {count}"
        except Exception as e:
            return f"[ERREUR get_record_count sur {model}]: {e}"


    @api.model
    def run_agent_loop(self, user_question: str, config, session=None) -> tuple:
        intent = self._classify_question(user_question)
        _logger.info(f"[AI Agent v4] Intent: {intent}, user={self.env.uid}")

        if intent['is_chitchat']:
            return self._handle_chitchat(user_question, config), ""

        return self._handle_data_query(user_question, intent, config, session=session)

    @api.model
    def _handle_chitchat(self, question: str, config) -> str:
        lang_instruction = LANG_LABELS.get(config.language, LANG_LABELS['fr'])
        today  = date.today().isoformat()
        prompt = (
            f"{config.system_prompt}\n"
            f"{lang_instruction}\n\n"
            f"Date d'aujourd'hui : {today}\n\n"
            f"Utilisateur : {question}\n\n"
            "Assistant :"
        )
        try:
            raw = config.generate_raw(prompt)
            return self._clean_response(raw)
        except Exception as e:
            return f"Bonjour ! Comment puis-je vous aider ? (Erreur LLM : {e})"

    @api.model
    def _handle_data_query(self, question: str, intent: dict, config, session=None) -> tuple:
        today             = date.today().isoformat()
        lang_instruction  = LANG_LABELS.get(config.language, LANG_LABELS['fr'])
        candidate_models  = intent.get('candidate_models', [])
        needs_aggregate   = intent.get('needs_aggregate', False)

        candidate_schema = self._get_candidate_schema(candidate_models)

        plan = self._planning_step(question, candidate_schema, config)

        if plan['success']:
            _logger.info(f"[AI Agent v4] Plan validé: {plan['models']}")
            odoo_schema   = self._get_schema_for_models(plan['models'])
            planned_fields = plan['fields_map']
            planned_strategy = plan.get('strategy', 'search')
            planned_groupby  = plan.get('groupby', [])
            planned_order    = plan.get('order', None)
            planning_note = self._build_planning_note(plan, needs_aggregate)
        else:
            _logger.warning("[AI Agent v4] Planning échoué, fallback PRIORITY_FIELDS")
            odoo_schema      = candidate_schema
            planned_fields   = {}
            planned_strategy = 'aggregate' if needs_aggregate else 'search'
            planned_groupby  = []
            planned_order    = None
            planning_note    = self._build_aggregate_hint(needs_aggregate)

        history_block = ""
        if session:
            history_block = self._build_history_block(session, max_turns=MAX_HISTORY_TURNS)

        system_prompt = f"""{config.system_prompt}
{lang_instruction}

=== ACCÈS DONNÉES ODOO (READ-ONLY) ===
Date : {today}
{planning_note}
--- OUTILS DISPONIBLES ---
TOOL_CALL: {{"tool": "search_records",    "args": {{"model": "...", "domain": [...], "fields": [...], "limit": 20, "order": "..."}}}}
TOOL_CALL: {{"tool": "aggregate_records", "args": {{"model": "...", "domain": [...], "fields": ["champ:sum","id:count"], "groupby": ["champ_groupby"]}}}}
TOOL_CALL: {{"tool": "get_record_count",  "args": {{"model": "...", "domain": [...]}}}}
TOOL_CALL: {{"tool": "get_model_fields",  "args": {{"model": "..."}}}}

--- RÈGLES ---
1. Utilise les modèles et champs du PLAN ci-dessus — ils ont été validés sur ce serveur.
2. aggregate_records pour les totaux/stats, search_records pour les listes.
3. Domaines Odoo : [["champ", "op", "valeur"]] (op: =,!=,<,>,<=,>=,ilike,in).
4. Dates au format "YYYY-MM-DD".
5. Enchaîne plusieurs TOOL_CALL si besoin (ex: sale.order puis sale.order.line).
6. Réponds clairement en te basant UNIQUEMENT sur les données reçues.
7. Ne fabrique JAMAIS de données.

--- SCHÉMA DES MODÈLES RETENUS ---
{odoo_schema}
Construit la note de planning à injecter dans le system prompt ReAct."""
        lines = ["⚡ PLAN VALIDÉ PAR L'ANALYSE DE LA QUESTION :"]
        for model_name, fields in plan['fields_map'].items():
            lines.append(f"   • {model_name} → champs : {', '.join(fields)}")

        strategy = plan.get('strategy', 'search')
        if strategy == 'aggregate':
            groupby = plan.get('groupby', [])
            lines.append(
                f"\n   Stratégie : AGGREGATE (read_group) — groupby: {groupby}\n"
                "   Utilise aggregate_records avec fields=['champ:sum', 'id:count']."
            )
        else:
            order = plan.get('order')
            lines.append(f"\n   Stratégie : SEARCH — order: {order or 'défaut'}")

        return "\n".join(lines)

    def _build_aggregate_hint(self, needs_aggregate: bool) -> str:
        if needs_aggregate:
            return (
                "\n⚡ CONSEIL : La question demande des totaux ou statistiques.\n"
                "   Utilise TOUJOURS aggregate_records plutôt que search_records.\n"
                "   Exemple : fields=[\"amount_total:sum\", \"id:count\"], groupby=[]\n"
            )
        return ""

    def _build_history_block(self, session, max_turns: int = 4) -> str:
        try:
            msgs = session.message_ids.sorted('create_date')
            msgs = [m for m in msgs if m.role in ('user', 'assistant') and not m.is_error]
            msgs = msgs[:-1] if msgs else []
            msgs = msgs[-(max_turns * 2):]
            if not msgs:
                return ""
            lines = []
            for m in msgs:
                label   = "Utilisateur" if m.role == 'user' else "Assistant"
                content = (m.content or '')[:300]
                lines.append(f"{label}: {content}")
            return "\n".join(lines)
        except Exception as e:
            _logger.warning(f"[AI Agent v4] _build_history_block error: {e}")
            return ""

    def _extract_tool_calls(self, text: str) -> list:
        tool_calls = []
        if 'TOOL_CALL' in text.upper():
            _logger.info(f"[AI Agent v4] LLM raw text: |{text[:600]}|")
        pattern = r'TOOL_CALL:\s*(\{)'
        for m in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
            start  = m.start(1)
            depth  = 0
            end    = start
            in_str = False
            escape = False
            for i, ch in enumerate(text[start:], start=start):
                if escape:
                    escape = False
                    continue
                if ch == '\\' and in_str:
                    escape = True
                    continue
                if ch == '"' and not escape:
                    in_str = not in_str
                    continue
                if in_str:
                    continue
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            json_str = text[start:end]
            cleaned = re.sub(r'\n\s*', ' ', json_str)
            cleaned = cleaned.replace('\u201c', '"').replace('\u201d', '"') \
                              .replace('\u2018', "\'").replace('\u2019', "\'")
            cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
            cleaned = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', cleaned)
            cleaned = re.sub(r'//[^\n"]*', '', cleaned)
            try:
                tc = json.loads(cleaned)
                if 'tool' in tc:
                    tool_calls.append(tc)
            except json.JSONDecodeError:
                try:
                    tool_m = re.search(r'"tool"\s*:\s*"([^"]+)"', cleaned)
                    args_m = re.search(r'"args"\s*:\s*(\{.*\})', cleaned)
                    if tool_m:
                        tool_name = tool_m.group(1)
                        args = {}
                        if args_m:
                            try:
                                args = json.loads(args_m.group(1))
                            except Exception:
                                pass
                        tool_calls.append({'tool': tool_name, 'args': args})
                        _logger.warning(f"[AI Agent v4] TOOL_CALL récupéré par fallback : {tool_name}")
                    else:
                        _logger.warning(f"[AI Agent v4] TOOL_CALL JSON invalide (no tool key) RAW=|{cleaned[:400]}|")
                except Exception as fe:
                    _logger.warning(f"[AI Agent v4] TOOL_CALL JSON invalide (fallback err={fe}) RAW=|{cleaned[:400]}|")
        return tool_calls

    def _clean_response(self, text: str) -> str:
        text = re.sub(r'TOOL_CALL:\s*\{(?:[^{}]|\{[^{}]*\})*\}', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'TOOL_CALL[:\s]*', '', text, flags=re.IGNORECASE)
        lines   = [l for l in text.split("\n") if not re.match(r'\s*```', l)]
        cleaned = "\n".join(lines).strip()

        html_entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>',
            '&nbsp;': ' ', '&quot;': '"', '&#39;': "'",
        }
        for entity, char in html_entities.items():
            cleaned = cleaned.replace(entity, char)

        cleaned = re.sub(r'<br\s*/?>', '\n', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'</p>',      '\n', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'</div>',    '\n', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'</li>',     '\n', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'<[^>]+>',   '',  cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        return cleaned.strip()

    def _build_sources_summary(self, tool_calls: list, tool_results: list) -> str:
        if not tool_calls:
            return ""
        parts = []
        for i, tc in enumerate(tool_calls):
            model   = tc.get('args', {}).get('model', tc.get('tool', '?'))
            preview = tool_results[i][:200] if i < len(tool_results) else ''
            parts.append(f"[{tc.get('tool')}] {model}:\n{preview}")
        return "\n\n".join(parts)


    @api.model
    def detect_intent_and_fetch(self, question: str) -> str:
        return f"[Schéma Odoo – {date.today().isoformat()}]\n" + \
               self._get_odoo_schema(max_models=40)