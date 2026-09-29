/** @odoo-module **/

import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useChart } from "@web/core/utils/chart_hook";

const COLORS = ["#714B67", "#00A09D", "#E46E78", "#F0AD4E", "#5B7DB1", "#8BC34A", "#9E9E9E"];

export class QmsCockpit extends Component {
    static template = "qms_dashboard.Cockpit";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.cockpit = { data: null };
        this.coverageChart = useChart(() => this.coverageConfig());
        this.ncrChart = useChart(() => this.ncrConfig());
        this.monthlyChart = useChart(() => this.monthlyConfig());
        this.complaintChart = useChart(() => this.complaintConfig());
        onWillStart(async () => {
            this.cockpit.data = await this.orm.call("qms.dashboard", "get_dashboard_data", []);
        });
    }

    open(model, domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
            name: name || model,
            target: "current",
        });
    }

    baseOptions(extra) {
        return Object.assign(
            { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
            extra || {}
        );
    }

    coverageConfig() {
        const c = (this.cockpit.data && this.cockpit.data.charts.coverage) || { labels: [], data: [] };
        return {
            type: "doughnut",
            data: { labels: c.labels, datasets: [{ data: c.data, backgroundColor: COLORS }] },
            options: this.baseOptions({ cutout: "65%" }),
        };
    }

    ncrConfig() {
        const c = (this.cockpit.data && this.cockpit.data.charts.ncr_status) || { labels: [], data: [] };
        return {
            type: "bar",
            data: { labels: c.labels, datasets: [{ data: c.data, backgroundColor: COLORS }] },
            options: this.baseOptions({ plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }),
        };
    }

    monthlyConfig() {
        const c = (this.cockpit.data && this.cockpit.data.charts.monthly) || { labels: [], ncr: [], audits: [] };
        return {
            type: "bar",
            data: {
                labels: c.labels,
                datasets: [
                    { label: "NCRs", data: c.ncr, backgroundColor: "#E46E78" },
                    { label: "Audits", data: c.audits, backgroundColor: "#5B7DB1" },
                ],
            },
            options: this.baseOptions({ scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }),
        };
    }

    complaintConfig() {
        const c = (this.cockpit.data && this.cockpit.data.charts.complaints) || { labels: [], data: [] };
        return {
            type: "doughnut",
            data: { labels: c.labels, datasets: [{ data: c.data, backgroundColor: COLORS }] },
            options: this.baseOptions({ cutout: "65%" }),
        };
    }
}

registry.category("actions").add("qms_dashboard_cockpit", QmsCockpit);
