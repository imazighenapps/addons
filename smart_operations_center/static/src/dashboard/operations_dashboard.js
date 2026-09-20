/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class OperationsDashboard extends Component {
    static template = "smart_operations_center.OperationsDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: {
                by_severity: [], by_state: [], impact_by_type: [], activity: [],
                top_issues: [], overdue_list: [], baselines: [],
            },
        });
        onWillStart(() => this.load());
    }

    async load() {
        this.state.loading = true;
        this.state.data = await this.orm.call("smart.operations.issue", "get_dashboard_data", []);
        this.state.loading = false;
    }

    openIssues(domain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Operational Issues",
            res_model: "smart.operations.issue",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
            target: "current",
        });
    }

    openOpen() {
        this.openIssues([["state", "not in", ["resolved", "ignored"]]]);
    }

    openCritical() {
        this.openIssues([["severity", "=", "critical"], ["state", "not in", ["resolved", "ignored"]]]);
    }

    openEscalated() {
        this.openIssues([["state", "=", "escalated"]]);
    }

    openOverdueActions() {
        this.action.doAction("smart_operations_center.action_operations_actions");
    }

    openIssue(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "smart.operations.issue",
            views: [[false, "form"]],
            res_id: id,
            target: "current",
        });
    }

    openBaseline(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "smart.operations.baseline",
            views: [[false, "form"]],
            res_id: id,
            target: "current",
        });
    }

    maxOf(values) {
        return Math.max(...values.map((v) => Number(v || 0)), 1);
    }

    barHeight(value, series) {
        const max = this.maxOf(series.map((s) => s.value));
        return Math.max(8, Math.round((Number(value || 0) / max) * 100));
    }

    hbarWidth(value, series) {
        const max = this.maxOf(series.map((s) => s.value));
        return Math.max(4, Math.round((Number(value || 0) / max) * 100));
    }

    actHeight(point, key) {
        const series = (this.state.data.activity || []).map((a) => a[key]);
        return Math.max(6, Math.round((Number(point[key] || 0) / this.maxOf(series)) * 100));
    }

    donutTotal(segments) {
        return (segments || []).reduce((s, x) => s + Number(x.value || 0), 0) || 1;
    }

    donutPct(value, segments) {
        return Math.round((Number(value || 0) / this.donutTotal(segments)) * 100);
    }

    donutStyle(segments) {
        const palette = ["#2f7bd8", "#7b59d8", "#f1ae3d", "#e45b5b"];
        let cursor = 0;
        const total = this.donutTotal(segments);
        const parts = (segments || []).map((seg, index) => {
            const start = cursor;
            cursor += (Number(seg.value || 0) / total) * 100;
            return `${palette[index % palette.length]} ${start}% ${cursor}%`;
        });
        return `background: conic-gradient(${parts.join(",")})`;
    }

    fmtMoney(value) {
        return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(Number(value || 0));
    }
}

registry.category("actions").add("smart_operations_center.dashboard", OperationsDashboard);
