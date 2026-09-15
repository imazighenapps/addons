/** @odoo-module */

import { Component, onWillStart, useState } from '@odoo/owl';
import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

export class GuardianDashboard extends Component {
    static template = 'fs_configuration_guardian.GuardianDashboard';
    
    setup() {
        console.log("GuardianDashboard loaded");
        this.orm = useService('orm');
        this.action = useService('action');
        this.notification = useService('notification');
        this.state = useState({ loading: true, data: null, error: null, period: '7d' });
        onWillStart(async () => this.loadDashboard());
    }

    async loadDashboard() {
        console.log("loadDashboard loaded");
        this.state.loading = true;
        try {
            this.state.data = await this.orm.call('fs.guardian.baseline', 'get_dashboard_data', []);
            this.state.error = null;
        } catch (error) {
            this.state.error = error.message || 'Unable to load the dashboard.';
            this.notification.add(this.state.error, { type: 'danger' });
        } finally {
            this.state.loading = false;
        }
    }

    refresh() {
        return this.loadDashboard();
    }

   openChanges = (domain = []) => {
        if (!Array.isArray(domain)) {
            domain = [];
        }

        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Configuration Changes',
            res_model: 'fs.guardian.change',
            views: [[false, 'list'], [false, 'form']],
            domain: [
                ['company_id', '=', this.state.data.company.id],
                ...domain,
            ],
        });
    };

    openBaselines() {
        console.log("openBaselines loaded");
        return this.action.doAction('fs_configuration_guardian.action_guardian_baselines');
    }

    openSnapshots() {
        return this.action.doAction('fs_configuration_guardian.action_guardian_snapshots');
    }

    openRules() {
        return this.action.doAction('fs_configuration_guardian.action_guardian_rules');
    }

    openChange(id) {
        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Configuration Change',
            res_model: 'fs.guardian.change',
            res_id: id,
            views: [[false, 'form']],
        });
    }

    formatDate(value) {
        if (!value) return '—';
        const date = new Date(value.replace(' ', 'T') + 'Z');
        if (Number.isNaN(date.getTime())) return value;
        return new Intl.DateTimeFormat(undefined, { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }).format(date);
    }

    shortDate(value) {
        const date = new Date(value + 'T00:00:00');
        return new Intl.DateTimeFormat(undefined, { weekday: 'short' }).format(date);
    }

    get maxCategory() {
        return Math.max(...(this.state.data?.categories || []).map((x) => x.value), 1);
    }

    categoryWidth(value) {
        return `${Math.max(6, Math.round((value / this.maxCategory) * 100))}%`;
    }

    get trendMax() {
        return Math.max(...(this.state.data?.trend || []).map((x) => x.value), 1);
    }

    trendHeight(value) {
        return `${Math.max(8, Math.round((value / this.trendMax) * 100))}%`;
    }

    riskClass(level) {
        return `guardian-risk guardian-risk-${level}`;
    }

    statusClass(status) {
        return `guardian-status guardian-status-${status}`;
    }
}

registry.category('actions').add('fs_configuration_guardian.dashboard', GuardianDashboard);
