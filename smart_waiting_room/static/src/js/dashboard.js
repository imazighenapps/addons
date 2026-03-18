/** @odoo-module **/
/* ═══════════════════════════════════════════════════════════════════════════
   Smart Waiting Room — OWL2 Dashboard Widget (Odoo 18)
   ═══════════════════════════════════════════════════════════════════════════ */

import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

// ── Live Queue Counter ─────────────────────────────────────────────────────

export class WrLiveCounter extends Component {
    static template = "smart_waiting_room.WrLiveCounter";
    static props = { roomId: Number };

    setup() {
        this.state = useState({ count: 0, loading: true });
        this._pollTimer = null;
    }

    async fetchCount() {
        try {
            const result = await rpc("/web/dataset/call_kw", {
                model: "waiting.room",
                method: "read",
                args: [[this.props.roomId], ["waiting_count", "in_service_count", "is_open"]],
                kwargs: {},
            });
            if (result && result[0]) {
                this.state.count   = result[0].waiting_count;
                this.state.isOpen  = result[0].is_open;
                this.state.loading = false;
            }
        } catch {
            this.state.loading = false;
        }
    }

    onMounted() {
        this.fetchCount();
        this._pollTimer = setInterval(() => this.fetchCount(), 5000);
    }

    onWillUnmount() {
        clearInterval(this._pollTimer);
    }
}

// ── Quick Add to Queue Form ────────────────────────────────────────────────

export class WrQuickAddWidget extends Component {
    static template = "smart_waiting_room.WrQuickAdd";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            name: '',
            priority: '0',
            visitor_type: 'walk_in',
            submitting: false,
            rooms: [],
            departments: [],
            selectedRoom: null,
            selectedDept: null,
        });
        this.nameRef = useRef("nameInput");
    }

    async onMounted() {
        await this.loadRooms();
    }

    async loadRooms() {
        const rooms = await this.orm.searchRead(
            "waiting.room",
            [["is_open", "=", true]],
            ["id", "name", "department_ids"]
        );
        this.state.rooms = rooms;
        if (rooms.length === 1) this.state.selectedRoom = rooms[0].id;
    }

    async onRoomChange(ev) {
        const roomId = parseInt(ev.target.value);
        this.state.selectedRoom = roomId;
        const room = this.state.rooms.find(r => r.id === roomId);
        if (room && room.department_ids.length) {
            const depts = await this.orm.searchRead(
                "waiting.room.department",
                [["id", "in", room.department_ids]],
                ["id", "name"]
            );
            this.state.departments = depts;
        } else {
            this.state.departments = [];
        }
    }

    async submitQuickAdd() {
        if (!this.state.name.trim() || !this.state.selectedRoom) return;
        this.state.submitting = true;
        try {
            const vals = {
                name: this.state.name.trim(),
                room_id: this.state.selectedRoom,
                priority: this.state.priority,
                visitor_type: this.state.visitor_type,
            };
            if (this.state.selectedDept) vals.department_id = this.state.selectedDept;
            await this.orm.create("waiting.room.line", [vals]);
            this.notification.add(
                `✓ ${this.state.name} added to queue`,
                { type: "success", sticky: false }
            );
            this.state.name         = '';
            this.state.priority     = '0';
            this.state.visitor_type = 'walk_in';
            if (this.nameRef.el) this.nameRef.el.focus();
        } catch (err) {
            this.notification.add("Could not add to queue", { type: "danger" });
        } finally {
            this.state.submitting = false;
        }
    }

    onKeyDown(ev) {
        if (ev.key === 'Enter') this.submitQuickAdd();
    }
}

// ── Dashboard Stats ────────────────────────────────────────────────────────

export class WrDashboardStats extends Component {
    static template = "smart_waiting_room.WrDashboardStats";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            stats: null,
            loading: true,
        });
        this._timer = null;
    }

    async fetchStats() {
        try {
            const today = new Date().toISOString().slice(0, 10);
            const [rooms, totalWaiting, totalDone, totalNoShow] = await Promise.all([
                this.orm.searchRead("waiting.room", [["active", "=", true]],
                    ["name", "waiting_count", "in_service_count",
                     "done_today_count", "avg_wait_time", "is_open"]),
                this.orm.searchCount("waiting.room.line",
                    [["state", "=", "waiting"]]),
                this.orm.searchCount("waiting.room.line",
                    [["state", "=", "done"],
                     ["done_time", ">=", today + " 00:00:00"]]),
                this.orm.searchCount("waiting.room.line",
                    [["state", "=", "no_show"],
                     ["check_in_time", ">=", today + " 00:00:00"]]),
            ]);
            this.state.stats = {
                rooms,
                totalWaiting,
                totalDone,
                totalNoShow,
                noShowRate: totalDone + totalNoShow > 0
                    ? Math.round((totalNoShow / (totalDone + totalNoShow)) * 100)
                    : 0,
            };
        } catch (e) {
            console.warn("WR Dashboard stats error", e);
        } finally {
            this.state.loading = false;
        }
    }

    onMounted() {
        this.fetchStats();
        this._timer = setInterval(() => this.fetchStats(), 10000);
    }

    onWillUnmount() { clearInterval(this._timer); }
}

// Register as action client
registry.category("actions").add("wr_dashboard", WrDashboardStats);
