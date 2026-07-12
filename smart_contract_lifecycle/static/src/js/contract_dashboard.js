/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { Component, useState, useRef, onWillStart, onMounted, onPatched, onWillUnmount } from "@odoo/owl";

const TYPE_PALETTE = [
    "#C9A227", "#3E6E92", "#2F7D5C", "#B3433E",
    "#8A6FB3", "#C9852B", "#5B6472", "#1F3057",
];

const RISK_HEX = { low: "#2F7D5C", medium: "#C9852B", high: "#B3433E" };

class ContractDashboard extends Component {
    static template = "smart_contract_lifecycle.ContractDashboard";
    // static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.trendChartRef = useRef("trendChart");
        this.donutChartRef = useRef("donutChart");
        this.gaugeChartRef = useRef("gaugeChart");
        this.bubbleChartRef = useRef("bubbleChart");

        this.charts = {};
        this._activeContracts = [];
        this._chartsRendered = false;

        this.state = useState({
            loading: true,
            period: "year",
            today: new Intl.DateTimeFormat("en-US", {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
            }).format(new Date()),
            stats: this._emptyStats(),
        });

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            this._setChartDefaults();
            await this._loadStats();
        });

        onMounted(() => {
            if (!this.state.loading && !this._chartsRendered) {
                this._chartsRendered = true;
                this._renderCharts();
            }
        });

        onPatched(() => {
            if (!this.state.loading && !this._chartsRendered) {
                this._chartsRendered = true;
                this._renderCharts();
            }
        });

        onWillUnmount(() => {
            for (const key in this.charts) {
                if (this.charts[key]) {
                    this.charts[key].destroy();
                }
            }
        });
    }

    _setChartDefaults() {
        if (!window.Chart) return;
        window.Chart.defaults.font.family =
            "ui-monospace, SFMono-Regular, 'Roboto Mono', Consolas, monospace";
        window.Chart.defaults.font.size = 11.5;
        window.Chart.defaults.color = "#5B6472";
    }

    _emptyStats() {
        return {
            active: 0,
            expiring: 0,
            expired: 0,
            draft: 0,
            pending_approval: 0,
            total_count: 0,
            total_value: 0,
            currency_symbol: "",
            mrr: 0,
            arr: 0,
            renewal_rate: 0,
            avg_contract_value: 0,
            high_risk_count: 0,
            health: [],
            risk: [],
            watchlist: [],
            insights: [],
            donut: { labels: [], data: [], colors: [] },
            bubble: { low: [], medium: [], high: [] },
            health_score: 0,
            health_color: "success",
            active_ratio: 0,
            low_risk_ratio: 0,
            value_delta_pct: 0,
            value_delta_abs: 0,
            value_delta_up: true,
            count_delta_pct: 0,
            count_delta_abs: 0,
            count_delta_up: true,
            delta_label: "",
        };
    }

    /** Maps a dashboard period key to its bucketing unit, window start
     * date, number of buckets, and the caption used on delta badges. */
    _periodConfig(period, contracts) {
        const now = new Date();
        if (period === "month") {
            const start = new Date(now);
            start.setDate(start.getDate() - 29);
            start.setHours(0, 0, 0, 0);
            return { unit: "day", start, count: 29, deltaLabel: "vs 30 days ago" };
        }
        if (period === "quarter") {
            const start = new Date(now);
            start.setDate(start.getDate() - 13 * 7);
            start.setHours(0, 0, 0, 0);
            return { unit: "week", start, count: 13, deltaLabel: "vs last quarter" };
        }
        if (period === "all") {
            let earliest = null;
            for (const c of contracts) {
                if (c.date_start) {
                    const d = new Date(c.date_start);
                    if (!earliest || d < earliest) earliest = d;
                }
            }
            const start = earliest
                ? new Date(earliest.getFullYear(), earliest.getMonth(), 1)
                : new Date(now.getFullYear(), now.getMonth() - 11, 1);
            const count = Math.max(1,
                (now.getFullYear() - start.getFullYear()) * 12 + (now.getMonth() - start.getMonth())
            );
            return { unit: "month", start, count, deltaLabel: "all-time growth" };
        }
        const start = new Date(now.getFullYear(), now.getMonth() - 11, 1);
        return { unit: "month", start, count: 11, deltaLabel: "vs last year" };
    }

    _bucketIndex(date, start, unit) {
        if (unit === "day") return Math.floor((date - start) / 86400000);
        if (unit === "week") return Math.floor((date - start) / (7 * 86400000));
        return (date.getFullYear() - start.getFullYear()) * 12 + (date.getMonth() - start.getMonth());
    }

    _bucketLabel(start, idx, unit) {
        const d = new Date(start);
        if (unit === "day") d.setDate(d.getDate() + idx);
        else if (unit === "week") d.setDate(d.getDate() + idx * 7);
        else d.setMonth(d.getMonth() + idx);
        if (unit === "month") {
            return new Intl.DateTimeFormat("en-US", { month: "short", year: "2-digit" }).format(d);
        }
        return new Intl.DateTimeFormat("en-US", { day: "numeric", month: "short" }).format(d);
    }

    /** Builds the cumulative active-portfolio value (and contract count)
     * trend for the selected period, used by the hero chart and by the
     * KPI delta badges (first bucket = value at period start, last = now). */
    _buildTrend(contracts, period) {
        const cfg = this._periodConfig(period, contracts);
        const { unit, start, count } = cfg;

        let baselineValue = 0, baselineCount = 0;
        const valueBuckets = new Array(count + 1).fill(0);
        const countBuckets = new Array(count + 1).fill(0);

        for (const c of contracts) {
            if (!c.date_start) continue;
            const d = new Date(c.date_start);
            const idx = this._bucketIndex(d, start, unit);
            if (idx < 0) {
                baselineValue += c.amount_total || 0;
                baselineCount += 1;
            } else if (idx <= count) {
                valueBuckets[idx] += c.amount_total || 0;
                countBuckets[idx] += 1;
            }
        }

        const labels = [];
        const data = [];
        const countData = [];
        let runningValue = baselineValue;
        let runningCount = baselineCount;
        for (let i = 0; i <= count; i++) {
            runningValue += valueBuckets[i];
            runningCount += countBuckets[i];
            data.push(Math.round(runningValue * 100) / 100);
            countData.push(runningCount);
            labels.push(this._bucketLabel(start, i, unit));
        }

        const deltaPct = data[0] > 0
            ? ((data[data.length - 1] - data[0]) / data[0]) * 100
            : (data[data.length - 1] > 0 ? 100 : 0);
        const countDeltaPct = countData[0] > 0
            ? ((countData[countData.length - 1] - countData[0]) / countData[0]) * 100
            : (countData[countData.length - 1] > 0 ? 100 : 0);

        return { labels, data, deltaPct, countDeltaPct, deltaLabel: cfg.deltaLabel };
    }

    _buildDonutData(byType) {
        const total = byType.reduce((sum, t) => sum + t.value, 0);
        if (!total) {
            return { labels: [], data: [], colors: [] };
        }
        return {
            labels: byType.map((t) => t.label),
            data: byType.map((t) => t.value),
            colors: byType.map((t, i) => TYPE_PALETTE[i % TYPE_PALETTE.length]),
        };
    }

    /** Groups active contracts by risk level for the risk/value bubble
     * chart: x = risk score, y = contract value, r = recurring revenue
     * weight (so high-MRR contracts stand out visually). */
    _buildBubbleData(contracts) {
        const groups = { low: [], medium: [], high: [] };
        for (const c of contracts) {
            const level = c.risk_level && c.risk_level in groups ? c.risk_level : "low";
            const r = Math.max(5, Math.min(26, 5 + Math.sqrt(c.mrr || 0) * 0.6));
            groups[level].push({
                x: c.risk_score || 0,
                y: c.amount_total || 0,
                r,
                label: c.name,
            });
        }
        return groups;
    }

    /** Generates short narrative insight chips from already-computed
     * stats, ordered by severity (danger > warning > info > success). */
    _buildInsights(s) {
        const insights = [];
        if (s.expired > 0) {
            insights.push({
                icon: "fa-times-circle", tone: "danger",
                text: `${s.expired} contract${s.expired > 1 ? "s" : ""} expired and need attention.`,
            });
        }
        if (s.high_risk_count > 0) {
            insights.push({
                icon: "fa-exclamation-triangle", tone: "danger",
                text: `${s.high_risk_count} active contract${s.high_risk_count > 1 ? "s are" : " is"} flagged as high risk.`,
            });
        }
        if (s.expiring > 0) {
            insights.push({
                icon: "fa-clock-o", tone: "warning",
                text: `${s.expiring} contract${s.expiring > 1 ? "s are" : " is"} expiring soon.`,
            });
        }
        if (s.pending_approval > 0) {
            insights.push({
                icon: "fa-hourglass-half", tone: "info",
                text: `${s.pending_approval} contract${s.pending_approval > 1 ? "s" : ""} waiting for approval.`,
            });
        }
        if (insights.length === 0) {
            insights.push({
                icon: "fa-check-circle", tone: "success",
                text: "Portfolio is healthy — no urgent items right now.",
            });
        }
        return insights.slice(0, 4);
    }

    async _loadStats() {
        try {
            const contracts = await this.orm.searchRead(
                "contract.contract",
                [["active", "=", true]],
                [
                    "name",
                    "partner_id",
                    "state",
                    "amount_total",
                    "is_near_expiry",
                    "currency_id",
                    "mrr",
                    "contract_type",
                    "date_start",
                    "date_end",
                    "risk_level",
                    "risk_score",
                ],
                { limit: false }
            );

            let active = 0, expiring = 0, expired = 0, draft = 0, pending = 0;
            let totalValue = 0;
            let currencySymbol = "";
            let mrr = 0;
            const byTypeMap = {};
            const riskCounts = { low: 0, medium: 0, high: 0 };
            let activeCount = 0;
            const watchPool = [];
            const activeContracts = [];

            for (const c of contracts) {
                if (c.currency_id && !currencySymbol) {
                    currencySymbol = c.currency_id[1] || "";
                }
                totalValue += c.amount_total || 0;
                mrr += c.mrr || 0;

                if (c.state === "active") {
                    activeCount++;
                    activeContracts.push(c);
                    const typeLabel = c.contract_type || "other";
                    byTypeMap[typeLabel] = (byTypeMap[typeLabel] || 0) + (c.amount_total || 0);

                    if (c.risk_level && c.risk_level in riskCounts) {
                        riskCounts[c.risk_level]++;
                    }
                    if (c.date_end) {
                        watchPool.push(c);
                    }
                }

                switch (c.state) {
                    case "active":
                        active++;
                        if (c.is_near_expiry) expiring++;
                        break;
                    case "expired":
                        expired++;
                        break;
                    case "draft":
                        draft++;
                        break;
                    case "pending_approval":
                        pending++;
                        break;
                }
            }

            const renewedCount = await this.orm.searchCount("contract.contract", [
                ["state", "=", "renewed"],
            ]);
            const lostCount = await this.orm.searchCount("contract.contract", [
                ["state", "in", ["expired", "cancelled"]],
            ]);
            const totalEnded = renewedCount + lostCount;
            const renewalRate = totalEnded > 0 ? (renewedCount / totalEnded) * 100 : 0;

            const avgContractValue = activeCount > 0 ? totalValue / activeCount : 0;

            const byType = Object.entries(byTypeMap)
                .map(([type, value]) => ({ type, value, label: this.contractTypeLabel(type) }))
                .sort((a, b) => b.value - a.value);

            const totalCount = active + expired + draft + pending;
            const healthSegments = [
                { key: "active", label: "Active", count: active, color: "success" },
                { key: "pending", label: "Pending Approval", count: pending, color: "info" },
                { key: "draft", label: "Draft", count: draft, color: "neutral" },
                { key: "expired", label: "Expired", count: expired, color: "danger" },
            ].map((seg) => ({
                ...seg,
                pct: totalCount > 0 ? (seg.count / totalCount) * 100 : 0,
            }));

            const riskOrder = [
                { key: "high", label: "High", color: "danger" },
                { key: "medium", label: "Medium", color: "warning" },
                { key: "low", label: "Low", color: "success" },
            ];
            const riskBreakdown = riskOrder.map((r) => ({
                ...r,
                count: riskCounts[r.key],
                pct: activeCount > 0 ? (riskCounts[r.key] / activeCount) * 100 : 0,
            }));

            const todayMidnight = new Date();
            todayMidnight.setHours(0, 0, 0, 0);
            const watchlist = watchPool
                .map((c) => {
                    const end = new Date(c.date_end);
                    end.setHours(0, 0, 0, 0);
                    const days = Math.round((end - todayMidnight) / 86400000);
                    let urgency = "ok";
                    if (days <= 7) urgency = "critical";
                    else if (days <= 30) urgency = "warning";
                    return {
                        id: c.id,
                        name: c.name,
                        partner_name: c.partner_id ? c.partner_id[1] : "",
                        amount_total: c.amount_total || 0,
                        days_remaining: days,
                        urgency,
                    };
                })
                .sort((a, b) => a.days_remaining - b.days_remaining)
                .slice(0, 5);

            const activeRatio = totalCount ? (active / totalCount) * 100 : 0;
            const lowRiskRatio = activeCount ? (riskCounts.low / activeCount) * 100 : 100;
            const healthScore = Math.max(0, Math.min(100, Math.round(
                activeRatio * 0.4 + lowRiskRatio * 0.35 + renewalRate * 0.25
            )));
            const healthColor = healthScore >= 70 ? "success" : healthScore >= 40 ? "warning" : "danger";

            this._activeContracts = activeContracts;
            const trend = this._buildTrend(activeContracts, this.state.period);

            const stats = {
                active,
                expiring,
                expired,
                draft,
                pending_approval: pending,
                total_count: totalCount,
                total_value: totalValue,
                currency_symbol: currencySymbol,
                mrr,
                arr: mrr * 12,
                renewal_rate: renewalRate,
                avg_contract_value: avgContractValue,
                high_risk_count: riskCounts.high,
                health: healthSegments,
                risk: riskBreakdown,
                watchlist,
                donut: this._buildDonutData(byType),
                bubble: this._buildBubbleData(activeContracts),
                health_score: healthScore,
                health_color: healthColor,
                active_ratio: activeRatio,
                low_risk_ratio: lowRiskRatio,
                value_delta_pct: trend.deltaPct,
                value_delta_abs: Math.abs(trend.deltaPct),
                value_delta_up: trend.deltaPct >= 0,
                count_delta_pct: trend.countDeltaPct,
                count_delta_abs: Math.abs(trend.countDeltaPct),
                count_delta_up: trend.countDeltaPct >= 0,
                delta_label: trend.deltaLabel,
            };
            stats.insights = this._buildInsights(stats);

            this._trendData = trend;
            this.state.stats = stats;
            this.state.loading = false;
        } catch (e) {
            console.error("ContractDashboard: failed to load stats", e);
            this.state.loading = false;
        }
    }

    async _setPeriod(period) {
        if (this.state.period === period) return;
        this.state.period = period;
        const trend = this._buildTrend(this._activeContracts, period);
        this._trendData = trend;
        this.state.stats.value_delta_pct = trend.deltaPct;
        this.state.stats.value_delta_abs = Math.abs(trend.deltaPct);
        this.state.stats.value_delta_up = trend.deltaPct >= 0;
        this.state.stats.count_delta_pct = trend.countDeltaPct;
        this.state.stats.count_delta_abs = Math.abs(trend.countDeltaPct);
        this.state.stats.count_delta_up = trend.countDeltaPct >= 0;
        this.state.stats.delta_label = trend.deltaLabel;
        if (this.charts.trend) {
            this.charts.trend.data.labels = trend.labels;
            this.charts.trend.data.datasets[0].data = trend.data;
            this.charts.trend.update();
        }
    }

    _renderCharts() {
        try {
            this._renderTrendChart();
            this._renderDonutChart();
            this._renderGaugeChart();
            this._renderBubbleChart();
        } catch (e) {
            console.error("ContractDashboard: failed to render charts", e);
        }
    }

    _renderTrendChart() {
        const el = this.trendChartRef.el;
        if (!el || !window.Chart || !this._trendData) return;
        const ctx = el.getContext("2d");
        const gradient = ctx.createLinearGradient(0, 0, 0, el.clientHeight || 160);
        gradient.addColorStop(0, "rgba(201,162,39,0.40)");
        gradient.addColorStop(1, "rgba(201,162,39,0)");

        this.charts.trend = new window.Chart(ctx, {
            type: "line",
            data: {
                labels: this._trendData.labels,
                datasets: [{
                    data: this._trendData.data,
                    borderColor: "#C9A227",
                    backgroundColor: gradient,
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: "#C9A227",
                    pointHoverBorderColor: "#14213D",
                    pointHoverBorderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: "index" },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#14213D",
                        titleColor: "#C9A227",
                        bodyColor: "#FFFFFF",
                        padding: 10,
                        displayColors: false,
                        callbacks: {
                            label: (c) => `${this.formatAmount(c.parsed.y)} ${this.state.stats.currency_symbol}`,
                        },
                    },
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: "#93A0BD", maxTicksLimit: 6, maxRotation: 0 },
                    },
                    y: { display: false },
                },
            },
        });
    }

    _renderDonutChart() {
        const el = this.donutChartRef.el;
        const donut = this.state.stats.donut;
        if (!el || !window.Chart || !donut.labels.length) return;
        this.charts.donut = new window.Chart(el.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: donut.labels,
                datasets: [{
                    data: donut.data,
                    backgroundColor: donut.colors,
                    borderColor: "#FFFFFF",
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "right",
                        labels: { boxWidth: 10, padding: 12, color: "#5B6472" },
                    },
                    tooltip: {
                        callbacks: {
                            label: (c) => ` ${c.label}: ${this.formatAmount(c.parsed)} ${this.state.stats.currency_symbol}`,
                        },
                    },
                },
            },
        });
    }

    _renderGaugeChart() {
        const el = this.gaugeChartRef.el;
        if (!el || !window.Chart) return;
        const score = this.state.stats.health_score;
        const color = RISK_HEX[
            this.state.stats.health_color === "success" ? "low"
            : this.state.stats.health_color === "warning" ? "medium" : "high"
        ];
        this.charts.gauge = new window.Chart(el.getContext("2d"), {
            type: "doughnut",
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [color, "#E5E1D6"],
                    borderWidth: 0,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                rotation: -90,
                circumference: 360,
                cutout: "72%",
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
            },
        });
    }

    _renderBubbleChart() {
        const el = this.bubbleChartRef.el;
        if (!el || !window.Chart) return;
        const groups = this.state.stats.bubble;
        if (!groups.low.length && !groups.medium.length && !groups.high.length) return;
        this.charts.bubble = new window.Chart(el.getContext("2d"), {
            type: "bubble",
            data: {
                datasets: [
                    { label: "Low risk", data: groups.low, backgroundColor: "rgba(47,125,92,0.55)", borderColor: "#2F7D5C" },
                    { label: "Medium risk", data: groups.medium, backgroundColor: "rgba(201,133,43,0.55)", borderColor: "#C9852B" },
                    { label: "High risk", data: groups.high, backgroundColor: "rgba(179,67,58,0.55)", borderColor: "#B3433E" },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: "Risk score", color: "#5B6472" },
                        min: 0, max: 100,
                        grid: { color: "#E5E1D6" },
                    },
                    y: {
                        title: { display: true, text: "Contract value", color: "#5B6472" },
                        grid: { color: "#E5E1D6" },
                        ticks: { callback: (v) => this.formatAmount(v) },
                    },
                },
                plugins: {
                    legend: { position: "bottom", labels: { boxWidth: 10, color: "#5B6472" } },
                    tooltip: {
                        callbacks: {
                            label: (c) => ` ${c.raw.label}: ${this.formatAmount(c.raw.y)} ${this.state.stats.currency_symbol} (risk ${c.raw.x})`,
                        },
                    },
                },
            },
        });
    }

    contractTypeLabel(type) {
        const labels = {
            customer: "Customer",
            supplier: "Vendor",
            partnership: "Partnership",
            nda: "NDA",
            employment: "Employment",
            lease: "Lease",
            service: "Service",
            other: "Other",
        };
        return labels[type] || type;
    }

    formatAmount(amount) {
        return new Intl.NumberFormat("en-US", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount);
    }

    formatPercent(value) {
        return new Intl.NumberFormat("en-US", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 1,
        }).format(value);
    }

    openContracts(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: "contract.contract",
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ],
            domain: domain,
            target: "current",
        });
    }

    openContract(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "contract.contract",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add(
    "smart_contract_lifecycle.contract_dashboard_action_client",
    ContractDashboard
);

export { ContractDashboard };