/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";

// ─────────────────────────────────────────────────────────────
// DASHBOARD ACTION
// ─────────────────────────────────────────────────────────────
class DuplicateDashboard extends Component {
    static template = "partner_duplicate_detector.Dashboard";
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: [Number, String], optional: true },
        updateActionState: { type: Function, optional: true },
        className: { type: String, optional: true },
    };

    setup() {
        // Rename to actionService to avoid collision with the 'action' prop
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            pending: 0,
            merged: 0,
            ignored: 0,
            affected: 0,
            scanning: false,
        });

        onWillStart(() => this.loadStats());
    }

    async loadStats() {
        try {
            const data = await this.orm.call(
                "partner.duplicate.group",
                "get_dashboard_data",
                []
            );
            this.state.pending = data.pending;
            this.state.merged = data.merged;
            this.state.ignored = data.ignored;
            this.state.affected = data.affected_partners;
        } catch (_e) {
            // silently fail
        }
    }

    async runScan() {
        this.state.scanning = true;
        try {
            const count = await this.orm.call(
                "partner.duplicate.group",
                "run_scan",
                []
            );
            await this.loadStats();
            this.notification.add(
                `Scan complete! ${count} new duplicate group(s) found.`,
                { type: "success", title: "Duplicate Detector", sticky: false }
            );
        } catch (_e) {
            this.notification.add(
                "Scan failed. Please try again.",
                { type: "danger", title: "Duplicate Detector" }
            );
        } finally {
            this.state.scanning = false;
        }
    }

    openPending()  { this._openGroups("pending");  }
    openAffected() { this._openGroups(null);        }
    openMerged()   { this._openGroups("merged");    }
    openIgnored()  { this._openGroups("ignored");   }

    _openGroups(state) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Duplicate Partners",
            res_model: "partner.duplicate.group",
            views: [[false, "list"], [false, "form"]],
            domain: state ? [["state", "=", state]] : [],
            context: {},
        });
    }
}

registry.category("actions").add(
    "partner_duplicate_detector.dashboard",
    DuplicateDashboard
);

// ─────────────────────────────────────────────────────────────
// SYSTRAY BADGE
// ─────────────────────────────────────────────────────────────
class DuplicateSystrayBadge extends Component {
    static template = "partner_duplicate_detector.SystrayBadge";
    static props = {};

    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.state = useState({ count: 0 });

        onWillStart(async () => {
            try {
                const count = await this.orm.searchCount(
                    "partner.duplicate.group",
                    [["state", "=", "pending"]]
                );
                this.state.count = count;
            } catch (_e) {
                this.state.count = 0;
            }
        });
    }

    openDuplicates() {
        this.actionService.doAction(
            "partner_duplicate_detector.action_duplicate_groups"
        );
    }
}

registry.category("systray").add(
    "partner_duplicate_detector.badge",
    { Component: DuplicateSystrayBadge },
    { sequence: 5 }
);