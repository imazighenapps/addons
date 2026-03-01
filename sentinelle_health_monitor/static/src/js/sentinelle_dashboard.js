/** @odoo-module **/
// sentinelle_health_monitor/static/src/components/dashboard/sentinelle_dashboard.js

import {
    Component,
    useState,
    onWillStart,
    onMounted,
    onWillUnmount,
    useRef,
    useEffect,
} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

// ─────────────────────────────────────────────────────────────────────────────
// Sub-component: KpiCard
// ─────────────────────────────────────────────────────────────────────────────
class KpiCard extends Component {
    static template = "sentinelle_health_monitor.KpiCard";
    static props = {
        label:    String,
        value:    { type: [Number, String] },
        unit:     { type: String,   optional: true },
        icon:     { type: String,   optional: true },
        variant:  { type: String,   optional: true },
        subtitle: { type: String,   optional: true },
        trend:    { type: String,   optional: true },   // "up" | "down" | ""
        onClick:  { type: Function, optional: true },
    };
    static defaultProps = { unit: "", icon: "●", variant: "neutral", subtitle: "", trend: "" };

    handleClick() {
        if (this.props.onClick) this.props.onClick();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-component: GaugeWidget — SVG half-circle gauge
// ─────────────────────────────────────────────────────────────────────────────
class GaugeWidget extends Component {
    static template = "sentinelle_health_monitor.GaugeWidget";
    static props = {
        value:             Number,
        label:             String,
        sublabel:          { type: String,  optional: true },
        thresholdWarning:  { type: Number,  optional: true },
        thresholdCritical: { type: Number,  optional: true },
    };
    static defaultProps = { thresholdWarning: 75, thresholdCritical: 90, sublabel: "" };

    get arcData() {
       const r = 50, cx = 60, cy = 62;
        // background arc: left to right (-180° to 0°)
        const bg = `M ${cx - r},${cy} A ${r},${r} 0 0,1 ${cx + r},${cy}`;
        // fill arc: proportional to value
        const pct = Math.min(100, Math.max(0, this.props.value)) / 100;
        const angleDeg  = pct * 180 - 180;          // -180° → 0°
        const angleRad  = (angleDeg * Math.PI) / 180;
        const x = cx + r * Math.cos(angleRad);
        const y = cy + r * Math.sin(angleRad);
        const largeArc  = pct > 1 ? 1 : 0;
        const fill = pct === 0
            ? `M ${cx - r},${cy}` // empty
            : `M ${cx - r},${cy} A ${r},${r} 0 ${largeArc},1 ${x},${y}`;
        return { bg, fill };
    }

    get color() {
        const v = this.props.value;
        if (v >= this.props.thresholdCritical) return "#ef4444";
        if (v >= this.props.thresholdWarning)  return "#f59e0b";
        return "#10b981";
    }

    get statusLabel() {
        const v = this.props.value;
        if (v >= this.props.thresholdCritical) return "Critical";
        if (v >= this.props.thresholdWarning)  return "Warning";
        return "Healthy";
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-component: AlertRow
// ─────────────────────────────────────────────────────────────────────────────
class AlertRow extends Component {
    static template = "sentinelle_health_monitor.AlertRow";
    static props = {
        alert:         Object,
        onAcknowledge: { type: Function, optional: true },
        onOpen:        { type: Function, optional: true },
    };

    get sevConfig() {
        return {
            critical: { icon: "●", cls: "snt-sev-critical", label: "Critical" },
            warning:  { icon: "◆", cls: "snt-sev-warning",  label: "Warning"  },
            info:     { icon: "○", cls: "snt-sev-info",     label: "Info"     },
        }[this.props.alert.severity] || { icon: "○", cls: "snt-sev-info", label: "Info" };
    }

    get timeAgo() {
        const raw = this.props.alert.create_date;
        if (!raw) return "";
        const d = new Date(raw.replace(" ", "T"));
        const m = Math.floor((Date.now() - d) / 60000);
        if (m < 1)  return "just now";
        if (m < 60) return `${m}m ago`;
        const h = Math.floor(m / 60);
        if (h < 24) return `${h}h ago`;
        return `${Math.floor(h / 24)}d ago`;
    }

    handleAck(ev) {
        ev.stopPropagation();
        if (this.props.onAcknowledge) this.props.onAcknowledge(this.props.alert.id);
    }
    handleOpen() {
        if (this.props.onOpen) this.props.onOpen(this.props.alert.id);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Dashboard Component
// ─────────────────────────────────────────────────────────────────────────────
export class SentinelleDashboard extends Component {
    static template   = "sentinelle_health_monitor.Dashboard";
    static components = { KpiCard, GaugeWidget, AlertRow };
    static display    = { controlPanel: {} };

    setup() {
        this.rpc    = rpc;
        this.action = useService("action");
        this.notif  = useService("notification");

        this.state = useState({
            loading: true,
            error: null,

            // ── KPIs (from main.py _kpis) ──────────────────────────────
            kpis: {
                open_critical: 0, open_warning: 0, total_open: 0,
                alerts_today: 0, resolved_today: 0, metrics_exceeded: 0,
                avg_orm_create: null, avg_orm_write: null, avg_orm_search: null,
                slow_sql_count: 0, api_failures: 0, log_errors_1h: 0,
                total_crons: 0, delayed_crons: 0, failing_crons: 0, cron_alerts_24h: 0,
            },

            // ── system_stats ────────────────────────────────────────────────
            resources: {
                cpu_pct: 0, ram_pct: 0, disk_pct: 0,
                ram_used_gb: 0, ram_total_gb: 0, disk_free_gb: 0,
                db_size_mb: 0, table_sizes: [],
            },

            // ── Derived lists ─────────────────────────────────────────────
            recentAlerts:   [],   // recent_alerts
            alertsByType:   [],   // alerts_by_type  → {label, value, color}
            alertTrend:     [],   // alert_trend      → {hour, count, critical, warning, info}

            // ── Performance ─────────────────────────────────────────────────
            ormCreate:      [],   // metric_history.orm_create  → {value, name}
            ormWrite:       [],   // metric_history.orm_write
            ormSearch:      [],   // metric_history.orm_search
            topSlowQueries: [],   // metric_history.sql_slow    → {value, sql_query_preview, name}
            apiEndpoints:   [],   // metric_history.api         → {value, name, endpoint}

            // ── Logs & Jobs ─────────────────────────────────────────────────
            topErrors:      [],   // metric_history.log_errors  → {model_name, value}
            cronStatus:     [],   // cron_stats                 → {id, name, nextcall, delay_minutes, failure_count, status}

            lastRefresh: null,
            activeTab:   "overview",
        });

        // Canvas refs for Chart.js
        this.canvasAlertType  = useRef("canvasAlertType");
        this.canvasAlertTrend = useRef("canvasAlertTrend");
        this.canvasOrm        = useRef("canvasOrm");
        this.canvasCpuSpark   = useRef("canvasCpuSpark");
        this.canvasRamSpark   = useRef("canvasRamSpark");
        this._charts = {};

        onWillStart(() => this._load());

        onMounted(() => {
            this._drawCharts();
            this._timer = setInterval(() => this._load(), 90_000);
        });

        useEffect(
            () => { if (!this.state.loading) this._drawCharts(); },
            () => [this.state.activeTab, this.state.loading, this.state.recentAlerts.length]
        );

        onWillUnmount(() => {
            clearInterval(this._timer);
            this._destroyAllCharts();
        });
    }

    // ─────────────────────────────────────────────────────────────────────
    // Data loading
    // ─────────────────────────────────────────────────────────────────────
    async _load() {
        try {
            const data = await this.rpc("/sentinelle/dashboard/data", {});
            if (data.error) throw new Error(data.error);
            this._apply(data);
            this.state.error = null;
        } catch (e) {
            console.error("[Sentinelle]", e);
            this.state.error = "Unable to load data. Check permissions or cron status.";
        } finally {
            this.state.loading     = false;
            this.state.lastRefresh = new Date().toLocaleTimeString("en-US");
        }
    }

    /**
     * Maps backend payload → OWL state.
     * All keys are aligned with what main.py actually returns.
     */
    _apply(d) {
        // ── KPIs ─────────────────────────────────────────────────────────
        Object.assign(this.state.kpis, d.kpis || {});

        // ── System resources ────────────────────────────────────────────
        Object.assign(this.state.resources, d.system_stats || {});

        // ── Recent alerts ──────────────────────────────────────────────
        this.state.recentAlerts = d.recent_alerts || [];

        // ── Distribution by type (field "value", not "count") ───────────
        this.state.alertsByType = d.alerts_by_type || [];

        // ── 24h trend (key "alert_trend", not "alert_trend_24h") ───────
        this.state.alertTrend = d.alert_trend || [];

        // ── ORM history ───────────────────────────────────────────────
        const mh = d.metric_history || {};
        this.state.ormCreate      = mh.orm_create  || [];
        this.state.ormWrite       = mh.orm_write   || [];
        this.state.ormSearch      = mh.orm_search  || [];

        // ── Slow SQL (field sql_query_preview) ───────────────────────
        this.state.topSlowQueries = mh.sql_slow || [];

        // ── API endpoints ─────────────────────────────────────────────
        this.state.apiEndpoints = mh.api || [];

        // ── Log errors ────────────────────────────────────────────────
        this.state.topErrors = mh.log_errors || [];

        // ── Cron jobs (key "cron_stats", field "delay_minutes") ──────
        this.state.cronStatus = d.cron_stats || [];
    }

    // ─────────────────────────────────────────────────────────────────────
    // Chart.js
    // ─────────────────────────────────────────────────────────────────────
    _destroyAllCharts() {
        for (const c of Object.values(this._charts)) {
            if (c) try { c.destroy(); } catch (_) {}
        }
        this._charts = {};
    }

    _destroyChart(key) {
        if (this._charts[key]) {
            try { this._charts[key].destroy(); } catch (_) {}
            this._charts[key] = null;
        }
    }

    _ctx(ref) {
        return ref && ref.el ? ref.el.getContext("2d") : null;
    }

    _drawCharts() {
        if (!window.Chart) return;
        requestAnimationFrame(() => {
            this._drawAlertType();
            this._drawAlertTrend();
            if (this.state.activeTab === "performance") {
                this._drawOrm();
            }
            if (this.state.activeTab === "system") {
                this._drawSparklines();
            }
        });
    }

    _chartDefaults() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    backgroundColor: "#0d1520",
                    titleColor: "#e2e8f0",
                    bodyColor: "#94a3b8",
                    borderColor: "#1e3a5f",
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                },
            },
        };
    }

    _drawAlertType() {
        this._destroyChart("alertType");
        const ctx  = this._ctx(this.canvasAlertType);
        const data = this.state.alertsByType;
        if (!ctx || !data.length) return;

        this._charts.alertType = new window.Chart(ctx, {
            type: "doughnut",
            data: {
                labels:   data.map(d => d.label),
                datasets: [{
                    // CORRECTION : le backend renvoie "value", pas "count"
                    data:            data.map(d => d.value),
                    backgroundColor: data.map(d => d.color),
                    borderWidth: 2,
                    borderColor: "#070d17",
                    hoverOffset: 12,
                }],
            },
            options: {
                ...this._chartDefaults(),
                cutout: "70%",
                plugins: {
                    ...this._chartDefaults().plugins,
                    legend: {
                        position: "bottom",
                        labels: {
                            color: "#64748b",
                            font: { size: 11, family: "'Space Grotesk', sans-serif" },
                            padding: 16,
                            boxWidth: 10,
                            boxHeight: 10,
                            usePointStyle: true,
                        },
                    },
                },
            },
        });
    }

    _drawAlertTrend() {
        this._destroyChart("alertTrend");
        const ctx  = this._ctx(this.canvasAlertTrend);
        const data = this.state.alertTrend;
        if (!ctx || !data.length) return;

        const labels = data.map(d => {
            const h = d.hour.substring(11, 13);
            return `${h}h`;
        });

        this._charts.alertTrend = new window.Chart(ctx, {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "Critical",
                        data: data.map(d => d.critical),
                        borderColor: "#ef4444",
                        backgroundColor: "rgba(239,68,68,0.08)",
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: "#ef4444",
                    },
                    {
                        label: "Warning",
                        data: data.map(d => d.warning),
                        borderColor: "#f59e0b",
                        backgroundColor: "rgba(245,158,11,0.06)",
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: "#f59e0b",
                    },
                    {
                        label: "Total",
                        data: data.map(d => d.count),
                        borderColor: "#3b82f6",
                        backgroundColor: "rgba(59,130,246,0.05)",
                        borderWidth: 1.5,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 2,
                        borderDash: [4, 4],
                    },
                ],
            },
            options: {
                ...this._chartDefaults(),
                interaction: { mode: "index", intersect: false },
                scales: {
                    x: {
                        grid: { color: "rgba(148,163,184,0.05)", drawBorder: false },
                        ticks: { color: "#475569", font: { size: 10 } },
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: "rgba(148,163,184,0.05)", drawBorder: false },
                        ticks: { color: "#475569", stepSize: 1, precision: 0 },
                    },
                },
                plugins: {
                    ...this._chartDefaults().plugins,
                    legend: {
                        labels: {
                            color: "#64748b",
                            font: { size: 11 },
                            boxWidth: 12,
                            usePointStyle: true,
                        },
                    },
                },
            },
        });
    }

    /**
     * CORRECTION : backend returns 3 separate arrays (orm_create, orm_write, orm_search),
     * each containing {value, name}. They are aligned by index (all 3 have max 30 entries).
     */
    _drawOrm() {
        this._destroyChart("orm");
        const ctx = this._ctx(this.canvasOrm);
        const c   = this.state.ormCreate;
        const w   = this.state.ormWrite;
        const s   = this.state.ormSearch;
        if (!ctx || (!c.length && !w.length && !s.length)) return;

        const len    = Math.max(c.length, w.length, s.length);
        const labels = Array.from({ length: len }, (_, i) => `#${i + 1}`);

        this._charts.orm = new window.Chart(ctx, {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "Create (ms)",
                        data: c.map(d => d.value),
                        borderColor: "#10b981",
                        backgroundColor: "rgba(16,185,129,0.08)",
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 3,
                        pointBackgroundColor: "#10b981",
                    },
                    {
                        label: "Write (ms)",
                        data: w.map(d => d.value),
                        borderColor: "#6366f1",
                        backgroundColor: "rgba(99,102,241,0.06)",
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 3,
                        pointBackgroundColor: "#6366f1",
                    },
                    {
                        label: "Search (ms)",
                        data: s.map(d => d.value),
                        borderColor: "#f59e0b",
                        backgroundColor: "rgba(245,158,11,0.06)",
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 3,
                        pointBackgroundColor: "#f59e0b",
                    },
                ],
            },
            options: {
                ...this._chartDefaults(),
                interaction: { mode: "index", intersect: false },
                scales: {
                    x: {
                        grid: { color: "rgba(148,163,184,0.05)", drawBorder: false },
                        ticks: { color: "#475569", font: { size: 10 } },
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: "rgba(148,163,184,0.05)", drawBorder: false },
                        ticks: { color: "#475569" },
                        title: { display: true, text: "ms", color: "#475569", font: { size: 11 } },
                    },
                },
                plugins: {
                    ...this._chartDefaults().plugins,
                    legend: {
                        labels: { color: "#64748b", font: { size: 11 }, boxWidth: 12, usePointStyle: true },
                    },
                },
            },
        });
    }

    _drawSparklines() {
        // Mini sparklines CPU/RAM via horizontal bars (in GaugeWidget)
        // Nothing to do here — SVG gauges re-render via OWL
    }

    // ─────────────────────────────────────────────────────────────────────
    // Navigation
    // ─────────────────────────────────────────────────────────────────────
    openAlerts(domain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sentinelle.alert",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
            name: "Sentinelle Alerts",
        });
    }

    openMetrics(domain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sentinelle.metric",
            view_mode: "list,graph,pivot,form",
            views: [[false, "list"], [false, "graph"], [false, "pivot"], [false, "form"]],
            domain: domain || [],
            name: "Sentinelle Metrics",
        });
    }

    async acknowledgeAlert(id) {
        try {
            await this.rpc("/sentinelle/alert/" + id + "/acknowledge", {});
            await this._load();
            this.notif.add("Alert acknowledged", { type: "success", sticky: false });
        } catch (_) {
            this.notif.add("Acknowledgement failed", { type: "danger", sticky: false });
        }
    }

    openAlertDetail(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sentinelle.alert",
            res_id: id,
            view_mode: "form",
            views: [[false, "form"]],
        });
    }

    async onRefresh() {
        this.state.loading = true;
        await this._load();
        this.notif.add("Dashboard refreshed", { type: "info", sticky: false });
    }

    setTab(tab) {
        this.state.activeTab = tab;
    }

    // ─────────────────────────────────────────────────────────────────────
    // Computed
    // ─────────────────────────────────────────────────────────────────────
    get healthStatus() {
        const { open_critical, open_warning } = this.state.kpis;
        if (open_critical > 0) return { label: "CRITICAL",  cls: "snt-health-critical", pulse: true };
        if (open_warning  > 0) return { label: "WARNING", cls: "snt-health-warning",  pulse: false };
        return                         { label: "HEALTHY",      cls: "snt-health-ok",       pulse: false };
    }

    get resolutionRate() {
        const t = this.state.kpis.alerts_today || 0;
        const r = this.state.kpis.resolved_today || 0;
        return t ? Math.round((r / t) * 100) : 100;
    }

    /** Formats avg_orm_* as short text */
    get ormSummary() {
        const k = this.state.kpis;
        const fmt = v => (v != null ? `${v} ms` : "N/A");
        return {
            create: fmt(k.avg_orm_create),
            write:  fmt(k.avg_orm_write),
            search: fmt(k.avg_orm_search),
        };
    }

    get cronSummary() {
        const k = this.state.kpis;
        const healthy = (k.total_crons || 0) - (k.delayed_crons || 0) - (k.failing_crons || 0);
        return { healthy: Math.max(0, healthy), delayed: k.delayed_crons || 0, failing: k.failing_crons || 0 };
    }
}

registry.category("actions").add("sentinelle_dashboard", SentinelleDashboard);
export default SentinelleDashboard;