/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


export class CFODashboardCockpit extends Component {
    async  setup() {

        this.orm = useService("orm"); 
        this.notification = useService("notification");
        this.state = useState({
            kpis: {},
            currency:"EUR",
            lang:"en-US",
            loading: true,
            error: null,
        });


        onWillStart(async () => {
            await this.loadKPIs();
            await this.getCurrency();
            await this.getLang();
        });

        onMounted(() => {
            // Refresh every 5 minutes
            this.refreshInterval = setInterval(() => {
                this.loadKPIs();
            }, 300000);
        });
    }

    async loadKPIs() {
        this.state.loading = true;
        this.state.error = null;
        try {
            const result = await this.orm.call(
                'cfo.kpi.engine',
                'compute_executive_kpis',
                [],
                {}
            );
            this.state.kpis = result;
            this.state.loading = false;
        } catch (error) {
            console.error("Error loading KPIs:", error);
            this.state.error = error.message || "Failed to load KPIs";
            this.state.loading = false;
            // this.notification.add(
            //     "Failed to load financial KPIs. Please check your configuration.",
            //     { type: "danger" }
            // );
        }
    }
    async getCurrency() {
        try {
            const result = await this.orm.call(
                'cfo.kpi.engine',
                'get_currency',
                [],
                {}
            );
            this.state.currency = result;
            
        } catch (error) {
            console.error("Error loading KPIs:", error);
        }
        
    }

    async getLang() {
        try {
            const result = await this.orm.call(
                'cfo.kpi.engine',
                'get_lang',
                [],
                {}
            );
            this.state.lang = result;
            
        } catch (error) {
            console.error("Error loading lang:", error);
        }
    }

    formatCurrency(value) {
        if (!value && value !== 0) return `${this.currency} 0.00`;
        return new Intl.NumberFormat(this.state.lang, {
            style: 'currency',
            currency: this.state.currency
        }).format(value);
    }


    formatNumber(value, decimals = 1) {
        if (!value && value !== 0) return '0';
        return Number(value).toFixed(decimals);
    }

    formatPercent(value) {
        if (!value && value !== 0) return '0%';
        return Number(value).toFixed(1) + '%';
    }

    async refreshDashboard() {
        await this.loadKPIs();
        this.notification.add("Dashboard refreshed successfully", { type: "success" });
    }
}

CFODashboardCockpit.template = "cfo_dashboard_pro.DashboardCockpit";

registry.category("actions").add("cfo_dashboard_cockpit", CFODashboardCockpit);
