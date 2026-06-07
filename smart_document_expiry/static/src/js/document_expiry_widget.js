/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { rpc } from '@web/core/network/rpc';

class DocumentExpiryDashboard extends Component {
    static template = "smart_document_expiry.Dashboard";

    setup() {
        this.rpc    = rpc;
        this.action = useService("action");

        this.state = useState({
            loading: true,
            // KPIs
            valid: 0, expiring: 0, expired: 0, renewed: 0,
            total: 0, compliance: 0, critical_count: 0,
            // Breakdowns
            by_entity: [], top_types: [],
            // Tables
            upcoming: [], recently_expired: [],
            // Alert pipeline
            alerts: { sent_90: 0, sent_30: 0, sent_7: 0, escalated: 0 },
            // UI
            activeTab: 'upcoming',
            currentTime: '',
        });

        onWillStart(async () => { await this._loadData(); });
        onMounted(() => { this._startClock(); });
    }

    // ── Clock ─────────────────────────────────────────────
    _startClock() {
        const update = () => {
            const now = new Date();
            this.state.currentTime = now.toLocaleTimeString('en-GB', {
                hour: '2-digit', minute: '2-digit', second: '2-digit',
            });
        };
        update();
        setInterval(update, 1000);
    }

    // ── Data loading ──────────────────────────────────────
    async _loadData() {
        try {
            const data = await this.rpc("/document_expiry/dashboard_data", {});
            Object.assign(this.state, data, { loading: false });
        } catch (e) {
            console.error("Document Expiry Dashboard: failed to load data", e);
            this.state.loading = false;
        }
    }

    async refreshData() {
        this.state.loading = true;
        await this._loadData();
    }

    // ── Tab switching — direct methods, no lambda, this is always bound ──
    setTabUpcoming() { this.state.activeTab = 'upcoming'; }
    setTabExpired()  { this.state.activeTab = 'expired';  }

    // ── Navigation ────────────────────────────────────────
    openAllDocuments() {
        this.action.doAction("smart_document_expiry.action_document_expiry");
    }
    openExpired() {
        this.action.doAction("smart_document_expiry.action_document_expiry_expired");
    }
    openExpiringSoon() {
        this.action.doAction("smart_document_expiry.action_document_expiry_soon");
    }
    openEntityDocs(entityType) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "document.expiry",
            view_mode: "list,kanban,form",
            domain: [["entity_type", "=", entityType]],
            name: this._entityLabel(entityType) + " — Documents",
        });
    }
    openDocument(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "document.expiry",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    // ── Compliance ring ───────────────────────────────────
    get ringCircumference() {
        return 2 * Math.PI * 52;
    }
    get ringOffset() {
        const pct = Math.min(Math.max(this.state.compliance, 0), 100);
        return this.ringCircumference - (pct / 100) * this.ringCircumference;
    }
    get ringColor() {
        const c = this.state.compliance;
        if (c >= 80) return "#10b981";
        if (c >= 50) return "#f59e0b";
        return "#ef4444";
    }
    get complianceLabel() {
        const c = this.state.compliance;
        if (c >= 80) return "Good";
        if (c >= 50) return "Fair";
        return "Critical";
    }
    get complianceLabelClass() {
        const c = this.state.compliance;
        if (c >= 80) return "ode-status-good";
        if (c >= 50) return "ode-status-warn";
        return "ode-status-crit";
    }

    // ── Bar widths ────────────────────────────────────────
    entityBarWidth(item, key) {
        if (!item.total) return 0;
        return Math.round((item[key] / item.total) * 100);
    }
    typeBarWidth(count) {
        const max = Math.max(...this.state.top_types.map(t => t.count), 1);
        return Math.round((count / max) * 100);
    }

    // ── Day badges ────────────────────────────────────────
    daysBadgeClass(days) {
        if (days < 0)   return "ode-badge ode-badge-expired";
        if (days <= 7)  return "ode-badge ode-badge-critical";
        if (days <= 30) return "ode-badge ode-badge-warn";
        return "ode-badge ode-badge-ok";
    }
    daysLabel(days) {
        if (days < 0)   return `${Math.abs(days)}d overdue`;
        if (days === 0) return "Today";
        if (days === 1) return "Tomorrow";
        return `${days}d left`;
    }
    daysOverLabel(d) {
        return `+${d}d`;
    }

    // ── Entity helpers ────────────────────────────────────
    entityIcon(type) {
        const map = {
            person:    'fa-user',
            vendor:    'fa-building',
            vehicle:   'fa-truck',
            equipment: 'fa-cog',
            other:     'fa-tag',
        };
        return map[type] || 'fa-file';
    }
    _entityLabel(type) {
        const map = {
            person:    'Persons',
            vendor:    'Vendors',
            vehicle:   'Vehicles',
            equipment: 'Equipment',
            other:     'Other',
        };
        return map[type] || type;
    }
    entityLabel(type) {
        return this._entityLabel(type);
    }

    // ── Date label ────────────────────────────────────────
    get todayLabel() {
        return new Date().toLocaleDateString('en-GB', {
            weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
        });
    }
}

registry.category("actions").add("document_expiry_dashboard", DocumentExpiryDashboard);
