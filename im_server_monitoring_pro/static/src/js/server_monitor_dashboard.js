/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from '@web/core/network/rpc';

// ─── Gauge Component ────────────────────────────────────────────────────────
class GaugeWidget extends Component {
    static template = "server_monitor.GaugeWidget";
    // static props = ["label", "value", "max", "unit", "status", "subtitle"];

    get percentage() {
        return Math.min((this.props.value / this.props.max) * 100, 100);
    }

    get strokeDashoffset() {
        const circumference = 2 * Math.PI * 54;
        return circumference - (this.percentage / 100) * circumference;
    }

    get color() {
        const colors = {
            success: "#28a745",
            warning: "#ffc107",
            danger:  "#dc3545",
        };
        return colors[this.props.status] || "#6c757d";
    }
}
GaugeWidget.template = owl.xml`
<div class="sm-gauge-card" t-att-class="'sm-status-' + props.status">
    <div class="sm-gauge-title"><t t-esc="props.label"/></div>
    <svg viewBox="0 0 120 120" class="sm-gauge-svg">
        <circle cx="60" cy="60" r="54" fill="none" stroke="#e9ecef" stroke-width="10"/>
        <circle cx="60" cy="60" r="54" fill="none"
            t-att-stroke="color"
            stroke-width="10"
            stroke-linecap="round"
            stroke-dasharray="339.3"
            t-att-stroke-dashoffset="strokeDashoffset"
            transform="rotate(-90 60 60)"
            style="transition: stroke-dashoffset 0.8s ease"/>
        <text x="60" y="58" text-anchor="middle" font-size="20" font-weight="bold"
              t-att-fill="color">
            <t t-esc="props.value.toFixed(1)"/>
        </text>
        <text x="60" y="75" text-anchor="middle" font-size="10" fill="#6c757d">
            <t t-raw="props.unit"/>
        </text>
    </svg>
    <div class="sm-gauge-subtitle"><t t-esc="props.subtitle"/></div>
</div>`;

// ─── Alert Badge ─────────────────────────────────────────────────────────────
class AlertBadge extends Component {
    static props = ["alert"];

    get icon() {
        return this.props.alert.severity === "critical" ? "🔴" : "🟡";
    }

    get cssClass() {
        return this.props.alert.severity === "critical"
            ? "sm-alert-critical"
            : "sm-alert-warning";
    }

    formatDate(dateStr) {
        try {
            return new Date(dateStr).toLocaleString("en-US");
        } catch {
            return dateStr;
        }
    }
}
AlertBadge.template = owl.xml`
<div t-att-class="'sm-alert-item ' + cssClass">
    <span class="sm-alert-icon"><t t-esc="icon"/></span>
    <div class="sm-alert-content">
        <div class="sm-alert-message"><t t-esc="props.alert.message"/></div>
        <div class="sm-alert-date"><t t-esc="formatDate(props.alert.date)"/></div>
    </div>
    <div class="sm-alert-value"><t t-esc="props.alert.value.toFixed(1)"/></div>
</div>`;

// ─── Process Row ──────────────────────────────────────────────────────────────
class ProcessRow extends Component {
    static props = ["process", "onKill"];

    get cpuClass() {
        const cpu = this.props.process.cpu_percent || 0;
        if (cpu >= 80) return "text-danger fw-bold";
        if (cpu >= 50) return "text-warning fw-bold";
        return "";
    }

    onKillClick() {
        this.props.onKill(this.props.process.pid, this.props.process.name);
    }
}
ProcessRow.template = owl.xml`
<tr>
    <td><code><t t-esc="props.process.pid"/></code></td>
    <td><strong><t t-esc="props.process.name"/></strong></td>
    <td><small class="text-muted"><t t-esc="props.process.username"/></small></td>
    <td t-att-class="cpuClass"><t t-esc="(props.process.cpu_percent || 0).toFixed(1)"/>%</td>
    <td><t t-esc="(props.process.memory_percent || 0).toFixed(1)"/>%</td>
    <td><t t-esc="(props.process.memory_mb || 0).toFixed(0)"/> MB</td>
    <td>
        <button class="btn btn-sm btn-outline-danger"
                t-on-click="onKillClick"
                title="Terminate this process">
            ⛔
        </button>
    </td>
</tr>`;

// ─── Main Dashboard ───────────────────────────────────────────────────────────
class ServerMonitorDashboard extends Component {
    static template = "server_monitor.Dashboard";
    static components = { GaugeWidget, AlertBadge, ProcessRow };
    
    setup() {
        this.rpc = rpc
        this.notification = useService("notification");
        this.historyChartRef = useRef("historyChart");
        this.networkChartRef = useRef("networkChart");
        this.cpuCoresChartRef = useRef("cpuCoresChart");

        this.state = useState({
            loading: true,
            error: null,
            data: null,
            historyPeriod: "24h",
            activeTab: "overview",
            refreshInterval: 10,
            lastRefresh: null,
            killConfirm: null,
        });

        this.historyChart = null;
        this.networkChart = null;
        this.cpuCoresChart = null;
        this.refreshTimer = null;

        onMounted(async () => {
            await this.loadData();
            this.startAutoRefresh();
        });

        onWillUnmount(() => {
            this.stopAutoRefresh();
            if (this.historyChart) this.historyChart.destroy();
            if (this.networkChart) this.networkChart.destroy();
            if (this.cpuCoresChart) this.cpuCoresChart.destroy();
        });
    }

    async loadData() {
        try {
            this.state.loading = true;
            const data = await this.rpc("/server_monitor/dashboard_data", {});
            if (data.error) throw new Error(data.error);
            this.state.data = data;
            this.state.error = null;
            this.state.lastRefresh = new Date().toLocaleTimeString("en-US");

            // Update charts after rendering
            setTimeout(() => {
                this.renderHistoryChart(data.history);
                this.renderCpuCoresChart(data.realtime.cpu_per_core || []);
                this.renderNetworkChart();
            }, 100);
        } catch (e) {
            this.state.error = e.message;
        } finally {
            this.state.loading = false;
        }
    }

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => this.loadData(), this.state.refreshInterval * 1000);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) clearInterval(this.refreshTimer);
    }

    async changeHistoryPeriod(period) {
        this.state.historyPeriod = period;
        try {
            const result = await this.rpc("/server_monitor/history", { period });
            if (result.data) this.renderHistoryChart(result.data);
        } catch (e) {
            console.error(e);
        }
    }

    async changeTab(tab) {
        this.state.activeTab = tab;
        if (tab === "network") {
            setTimeout(() => this.renderNetworkChart(), 100);
        }
    }

    // ─── Charts ────────────────────────────────────────────────────────────
    renderHistoryChart(history) {
        const canvas = this.historyChartRef.el;
        if (!canvas || !history || !history.length) return;

        if (this.historyChart) this.historyChart.destroy();

        const labels = history.map(h => {
            const d = new Date(h.timestamp);
            return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
        });

        this.historyChart = new Chart(canvas, {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "CPU %",
                        data: history.map(h => h.cpu),
                        borderColor: "#dc3545",
                        backgroundColor: "rgba(220,53,69,0.1)",
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0,
                    },
                    {
                        label: "RAM %",
                        data: history.map(h => h.ram),
                        borderColor: "#007bff",
                        backgroundColor: "rgba(0,123,255,0.1)",
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0,
                    },
                    {
                        label: "Disk %",
                        data: history.map(h => h.disk),
                        borderColor: "#28a745",
                        backgroundColor: "rgba(40,167,69,0.1)",
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: {
                    legend: { position: "top" },
                    tooltip: { mode: "index", intersect: false },
                },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { callback: v => v + "%" },
                        grid: { color: "rgba(0,0,0,0.05)" },
                    },
                    x: {
                        ticks: {
                            maxTicksLimit: 12,
                            maxRotation: 0,
                        },
                        grid: { display: false },
                    },
                },
            },
        });
    }

    renderCpuCoresChart(cores) {
        const canvas = this.cpuCoresChartRef.el;
        if (!canvas || !cores.length) return;

        if (this.cpuCoresChart) this.cpuCoresChart.destroy();

        const colors = cores.map(v =>
            v >= 90 ? "#dc3545" : v >= 70 ? "#ffc107" : "#28a745"
        );

        this.cpuCoresChart = new Chart(canvas, {
            type: "bar",
            data: {
                labels: cores.map((_, i) => `Core ${i}`),
                datasets: [{
                    label: "CPU per Core (%)",
                    data: cores,
                    backgroundColor: colors,
                    borderRadius: 4,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { callback: v => v + "%" },
                    },
                    x: { grid: { display: false } },
                },
            },
        });
    }

    renderNetworkChart() {
        const canvas = this.networkChartRef.el;
        const data = this.state.data;
        if (!canvas || !data) return;

        if (this.networkChart) this.networkChart.destroy();

        const interfaces = data.net_interfaces || [];
        const labels = interfaces.map(i => i.interface);
        const sendData = interfaces.map(i => i.speed_send || 0);
        const recvData = interfaces.map(i => i.speed_recv || 0);

        this.networkChart = new Chart(canvas, {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        label: "Upload (MB/s)",
                        data: sendData,
                        backgroundColor: "rgba(220,53,69,0.7)",
                        borderRadius: 4,
                    },
                    {
                        label: "Download (MB/s)",
                        data: recvData,
                        backgroundColor: "rgba(0,123,255,0.7)",
                        borderRadius: 4,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: { legend: { position: "top" } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => v + " MB/s" },
                    },
                    x: { grid: { display: false } },
                },
            },
        });
    }

    // ─── Kill Process ──────────────────────────────────────────────────────
    confirmKill(pid, name) {
        this.state.killConfirm = { pid, name };
    }

    cancelKill() {
        this.state.killConfirm = null;
    }

    async executeKill() {
        const { pid, name } = this.state.killConfirm;
        this.state.killConfirm = null;
        try {
            const result = await this.rpc("/server_monitor/kill_process", { pid, name });
            if (result.error) {
                this.notification.add(result.error, { type: "danger" });
            } else {
                this.notification.add(result.message || "Process terminated", { type: "success" });
                await this.loadData();
            }
        } catch (e) {
            this.notification.add("Error: " + e.message, { type: "danger" });
        }
    }

    // ─── Alerts ────────────────────────────────────────────────────────────
    async acknowledgeAlert(alertId) {
        try {
            await this.rpc("/server_monitor/acknowledge_alert", { alert_id: alertId });
            this.notification.add("Alert acknowledged", { type: "success" });
            await this.loadData();
        } catch (e) {
            this.notification.add("Error: " + e.message, { type: "danger" });
        }
    }

    // ─── Formatters ────────────────────────────────────────────────────────
    formatGB(gb) {
        return gb ? gb.toFixed(1) + " GB" : "—";
    }

    formatUptime(data) {
        if (!data) return "—";
        const { uptime_days, uptime_hours, uptime_minutes } = data;
        return `${uptime_days}d ${uptime_hours}h ${uptime_minutes}m`;
    }

    getStatusIcon(status) {
        const icons = { success: "🟢", warning: "🟡", danger: "🔴" };
        return icons[status] || "⚪";
    }
}


ServerMonitorDashboard.template = "server_monitor.Dashboard"


// ─── Register Dashboard ───────────────────────────────────────────────────────
registry.category("actions").add("server_monitor_dashboard", ServerMonitorDashboard);

// Load Chart.js dynamically if not available
// if (!window.Chart) {
//     const script = document.createElement("script");
//     script.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js";
//     document.head.appendChild(script);
// }
