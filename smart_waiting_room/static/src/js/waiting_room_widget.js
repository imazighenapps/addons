/** @odoo-module **/
/* ═══════════════════════════════════════════════════════════════════════════
   Smart Waiting Room — OWL2 Real-time Queue Widget (Odoo 19)
   ═══════════════════════════════════════════════════════════════════════════ */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * LiveQueueBoard — embeds a real-time kanban-style board into any view.
 * Usage: <WrLiveQueueBoard roomId="42" />
 */
export class WrLiveQueueBoard extends Component {
    static template = "smart_waiting_room.WrLiveQueueBoard";
    static props = {
        roomId: { type: Number, optional: true },
    };

    setup() {
        this.orm          = useService("orm");
        this.notification = useService("notification");
        this.action       = useService("action");
        this.state = useState({
            waiting:    [],
            called:     [],
            inService:  [],
            loading:    true,
            lastUpdate: null,
        });
        this._pollTimer = null;
    }

    async fetchQueue() {
        const domain = [["state", "in", ["waiting", "called", "in_service"]]];
        if (this.props.roomId) domain.push(["room_id", "=", this.props.roomId]);

        try {
            const lines = await this.orm.searchRead(
                "waiting.room.line",
                domain,
                ["id", "token_display", "name", "state", "priority",
                 "department_id", "wait_duration", "estimated_wait",
                 "is_late", "visitor_type", "call_count"],
                { order: "priority desc, sequence asc, token_number asc", limit: 50 }
            );
            this.state.waiting   = lines.filter(l => l.state === "waiting");
            this.state.called    = lines.filter(l => l.state === "called");
            this.state.inService = lines.filter(l => l.state === "in_service");
            this.state.lastUpdate = new Date().toLocaleTimeString();
        } catch {
            // silent
        } finally {
            this.state.loading = false;
        }
    }

    async callLine(lineId) {
        await this.orm.call("waiting.room.line", "action_call", [[lineId]]);
        this.notification.add("Patient called", { type: "success", sticky: false });
        await this.fetchQueue();
    }

    async startService(lineId) {
        await this.orm.call("waiting.room.line", "action_start_service", [[lineId]]);
        await this.fetchQueue();
    }

    async markDone(lineId) {
        await this.orm.call("waiting.room.line", "action_done", [[lineId]]);
        this.notification.add("Marked as done ✓", { type: "success", sticky: false });
        await this.fetchQueue();
    }

    async markNoShow(lineId) {
        await this.orm.call("waiting.room.line", "action_no_show", [[lineId]]);
        await this.fetchQueue();
    }

    openLine(lineId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "waiting.room.line",
            res_id: lineId,
            views: [[false, "form"]],
            target: "new",
        });
    }

    onMounted() {
        this.fetchQueue();
        this._pollTimer = setInterval(() => this.fetchQueue(), 4000);
    }

    onWillUnmount() {
        clearInterval(this._pollTimer);
    }

    get priorityLabel() {
        return { '0': '', '1': 'Priority', '2': 'Urgent', '3': 'VIP' };
    }
}

registry.category("components").add("WrLiveQueueBoard", WrLiveQueueBoard);
