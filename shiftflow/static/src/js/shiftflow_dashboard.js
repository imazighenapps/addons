/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ShiftFlowDashboard extends Component {
    static template = "shiftflow.ShiftFlowDashboard";
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ loading: true, data: {} });
        onWillStart(() => this.loadData());
    }
    async loadData() {
        this.state.loading = true;
        this.state.data = await this.orm.call("shiftflow.shift", "get_dashboard_data", []);
        this.state.loading = false;
    }
    refresh() {
        return this.loadData();
    }
    open(modelAction) {
        this.action.doAction(modelAction);
    }
    maxOf(values) {
        return Math.max(...values.map((v) => Number(v || 0)), 1);
    }
    barHeight(value, series) {
        const max = this.maxOf(series.map((s) => s.value));
        return Math.max(8, Math.round((Number(value || 0) / max) * 100));
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
        const palette = ["#e45b5b", "#f1ae3d", "#2f7bd8", "#22a06b", "#7b59d8"];
        let cursor = 0;
        const total = this.donutTotal(segments);
        const parts = (segments || []).map((seg, index) => {
            const start = cursor;
            cursor += (Number(seg.value || 0) / total) * 100;
            return `${palette[index % palette.length]} ${start}% ${cursor}%`;
        });
        return `background: conic-gradient(${parts.join(",")})`;
    }
}
registry.category("actions").add("shiftflow_dashboard", ShiftFlowDashboard);
