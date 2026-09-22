/** @odoo-module **/

import { Component, onWillStart, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";

const ACTION_TAG = "pestops_technician_app";

export class PestOpsTechnicianApp extends Component {
    static template = "pestops_core.PestOpsTechnicianApp";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            visits: [],
            selectedVisit: null,
            controlPoints: [],
            inspection: null,
            inspectionLines: {},
            inspectionPhoto: null,
            treatment: null,
            treatmentPhoto: null,
            treatmentLine: {
                product_id: null,
                lot_id: null,
                quantity: 1,
                location_id: null,
            },
            treatmentProducts: [],
            treatmentLots: [],
            stockLocations: [],
            view: "visits",
            online: navigator.onLine,
            signatureData: null,
            signerName: "",
            signatureNote: "",
            mobileDraftSaved: false,
        });

        this._onlineHandler = () => {
            this.state.online = true;
        };
        this._offlineHandler = () => {
            this.state.online = false;
        };
        window.addEventListener("online", this._onlineHandler);
        window.addEventListener("offline", this._offlineHandler);

        onWillStart(async () => {
            await this.loadVisits();
        });
        onWillUnmount(() => {
            window.removeEventListener("online", this._onlineHandler);
            window.removeEventListener("offline", this._offlineHandler);
        });
    }

    async loadVisits() {
        this.state.loading = true;
        try {
            const now = new Date();
            const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const end = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 2);

            const toOdooDatetime = (date) => {
                const pad = (n) => String(n).padStart(2, "0");
                return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} `
                    + `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
            };

            const visits = await this.orm.searchRead(
                "pest.visit",
                [
                    ["technician_id", "=", user.userId],
                    ["scheduled_start", ">=", toOdooDatetime(start)],
                    ["scheduled_start", "<", toOdooDatetime(end)],
                    ["state", "!=", "cancelled"],
                ],
                [
                    "id",
                    "name",
                    "site_id",
                    "plan_id",
                    "technician_id",
                    "scheduled_start",
                    "scheduled_end",
                    "actual_start",
                    "actual_end",
                    "state",
                    "priority",
                    "inspection_count",
                    "treatment_count",
                    "reservice_count",
                    "anomaly_count",
                "open_anomaly_count",
                "inspection_required",
                "treatment_required",
                "completion_outcome",
                "completion_summary",
                "notes",
                "mobile_checkin_used",
                "checkin_at",
                "checkout_at",
                "checkin_accuracy",
                "checkout_accuracy",
                "customer_signature_name",
                "customer_signature_date",
                "customer_signature",
                "customer_signature_note",
                "mobile_duration_minutes",
                ],
                {
                    order: "scheduled_start asc",
                    limit: 100,
                }
            );

            this.state.visits = visits;
        } catch (error) {
            this.notifyError("Unable to load today's visits.");
            throw error;
        } finally {
            this.state.loading = false;
        }
    }

    notifySuccess(message) {
        this.notification.add(message, { type: "success" });
    }

    notifyInfo(message) {
        this.notification.add(message, { type: "info" });
    }

    notifyError(message) {
        this.notification.add(message, { type: "danger" });
    }

    formatDateTime(value) {
        if (!value) {
            return "";
        }
        const date = new Date(value.replace(" ", "T") + "Z");
        return new Intl.DateTimeFormat(undefined, {
            day: "2-digit",
            month: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        }).format(date);
    }

    stateLabel(value) {
        return {
            draft: "Draft",
            scheduled: "Scheduled",
            in_progress: "In Progress",
            done: "Done",
            cancelled: "Cancelled",
        }[value] || value;
    }

    stateClass(value) {
        return `is-${value || "draft"}`;
    }

    async selectVisit(visit) {
        this.state.loading = true;
        try {
            const [fresh] = await this.orm.read(
                "pest.visit",
                [visit.id],
                [
                    "id",
                    "name",
                    "site_id",
                    "plan_id",
                    "technician_id",
                    "scheduled_start",
                    "scheduled_end",
                    "actual_start",
                    "actual_end",
                    "state",
                    "priority",
                    "inspection_count",
                    "treatment_count",
                    "reservice_count",
                    "anomaly_count",
                "open_anomaly_count",
                "inspection_required",
                "treatment_required",
                "completion_outcome",
                "completion_summary",
                "notes",
                "mobile_checkin_used",
                "checkin_at",
                "checkout_at",
                "checkin_accuracy",
                "checkout_accuracy",
                "customer_signature_name",
                "customer_signature_date",
                "customer_signature",
                "customer_signature_note",
                "mobile_duration_minutes",
                ]
            );

            this.state.selectedVisit = fresh;
            this.restoreMobileDraft();
            this.state.view = "visit";
            await this.loadVisitPoints();
        } catch (error) {
            this.notifyError("Unable to open the visit.");
            throw error;
        } finally {
            this.state.loading = false;
        }
    }

    async loadVisitPoints() {
        if (!this.state.selectedVisit?.site_id?.[0]) {
            this.state.controlPoints = [];
            return;
        }

        this.state.controlPoints = await this.orm.searchRead(
            "pest.control.point",
            [
                ["site_id", "=", this.state.selectedVisit.site_id[0]],
                ["active", "=", true],
            ],
            [
                "id",
                "name",
                "code",
                "zone_id",
                "point_type",
                "target_pest_ids",
                "last_inspection_date",
                "last_activity_level",
            ],
            {
                order: "zone_id asc, code asc",
                limit: 500,
            }
        );
    }

    async startVisit() {
        const location = await this.getCurrentLocation();
        if (!location) {
            return;
        }
        if (!this.state.online) {
            this.notifyError("You are offline. Check-in requires a connection.");
            return;
        }
        await this.orm.call("pest.visit", "action_mobile_check_in", [[this.state.selectedVisit.id], location.latitude, location.longitude, location.accuracy]);
        await this.refreshSelectedVisit();
        this.notifySuccess("Mobile check-in recorded.");
    }

    async scheduleVisit() {
        await this.orm.call("pest.visit", "action_schedule", [[this.state.selectedVisit.id]]);
        await this.refreshSelectedVisit();
        this.notifySuccess("Visit scheduled.");
    }

    async finishVisit() {
        if (this.state.selectedVisit.inspection_required && !this.state.selectedVisit.inspection_count) {
            this.notifyError("At least one inspection is required before finishing the visit.");
            return;
        }
        if (this.state.selectedVisit.treatment_required && !this.state.selectedVisit.treatment_count) {
            this.notifyError("At least one treatment is required before finishing the visit.");
            return;
        }
        this.state.signatureData = this.state.selectedVisit.customer_signature || null;
        this.state.signerName = this.state.selectedVisit.customer_signature_name || "";
        this.state.signatureNote = this.state.selectedVisit.customer_signature_note || "";
        this.state.mobileDraftSaved = false;
        this.state.view = "signature";
    }

    async refreshSelectedVisit() {
        await this.loadVisits();
        const currentId = this.state.selectedVisit.id;
        const fresh = this.state.visits.find((v) => v.id === currentId);
        if (fresh) {
            this.state.selectedVisit = fresh;
        }
        await this.loadVisitPoints();
        this.state.view = "visit";
    }

    openVisits() {
        this.state.view = "visits";
        this.state.selectedVisit = null;
        this.state.inspection = null;
        this.state.treatment = null;
    }

    async newInspection(point = null) {
        const values = {
            visit_id: this.state.selectedVisit.id,
        };

        const inspectionIds = await this.orm.create("pest.inspection", [values]);
        const inspectionId = inspectionIds[0];

        if (point) {
            await this.orm.create("pest.inspection.line", [{
                inspection_id: inspectionId,
                control_point_id: point.id,
                activity_level: point.last_activity_level || "none",
            }]);
        }

        this.state.inspection = {
            id: inspectionId,
            line_id: null,
        };
        this.state.inspectionLines = {};
        this.state.inspectionPhoto = null;

        const lines = await this.orm.searchRead(
            "pest.inspection.line",
            [["inspection_id", "=", inspectionId]],
            [
                "id",
                "control_point_id",
                "pest_id",
                "activity_level",
                "evidence",
                "action_required",
                "observation",
                "image_1920",
            ],
            { limit: 200 }
        );

        for (const line of lines) {
            this.state.inspectionLines[line.id] = {
                ...line,
                photoFile: null,
            };
        }

        this.state.view = "inspection";
    }

    async addAllPointsToInspection() {
        if (!this.state.inspection?.id) {
            await this.newInspection();
        }

        const existingLines = await this.orm.searchRead(
            "pest.inspection.line",
            [["inspection_id", "=", this.state.inspection.id]],
            ["control_point_id"],
            { limit: 500 }
        );

        const existing = new Set(existingLines.map((line) => line.control_point_id?.[0]));
        const values = this.state.controlPoints
            .filter((point) => !existing.has(point.id))
            .map((point) => ({
                inspection_id: this.state.inspection.id,
                control_point_id: point.id,
                activity_level: "none",
            }));

        if (values.length) {
            await this.orm.create("pest.inspection.line", values);
        }

        const lines = await this.orm.searchRead(
            "pest.inspection.line",
            [["inspection_id", "=", this.state.inspection.id]],
            [
                "id",
                "control_point_id",
                "pest_id",
                "activity_level",
                "evidence",
                "action_required",
                "observation",
                "image_1920",
            ],
            { limit: 500 }
        );

        this.state.inspectionLines = {};
        for (const line of lines) {
            this.state.inspectionLines[line.id] = {
                ...line,
                photoFile: null,
            };
        }
    }

    async saveInspection() {
        if (!this.state.inspection?.id) {
            return;
        }

        const inspectionVals = {};
        if (this.state.inspection.activity_level) {
            inspectionVals.activity_level = this.state.inspection.activity_level;
        }
        if (this.state.inspection.notes !== undefined) {
            inspectionVals.notes = this.state.inspection.notes || false;
        }
        if (this.state.inspectionPhoto) {
            inspectionVals.image_1920 = await this.fileToBase64(this.state.inspectionPhoto);
        }

        if (Object.keys(inspectionVals).length) {
            await this.orm.write("pest.inspection", [this.state.inspection.id], [inspectionVals]);
        }

        for (const line of Object.values(this.state.inspectionLines)) {
            const vals = {
                pest_id: line.pest_id?.[0] || false,
                activity_level: line.activity_level || "none",
                evidence: line.evidence || "none",
                action_required: !!line.action_required,
                observation: line.observation || false,
            };
            if (line.photoFile) {
                vals.image_1920 = await this.fileToBase64(line.photoFile);
            }
            await this.orm.write("pest.inspection.line", [line.id], [vals]);
        }

        this.notifySuccess("Inspection saved.");
        await this.refreshSelectedVisit();
        this.state.view = "visit";
    }

    onInspectionHeaderPhoto(event) {
        this.state.inspectionPhoto = event.target.files?.[0] || null;
    }

    onInspectionLinePhoto(lineId, event) {
        const file = event.target.files?.[0] || null;
        if (this.state.inspectionLines[lineId]) {
            this.state.inspectionLines[lineId].photoFile = file;
        }
    }

    async newTreatment() {
        const ids = await this.orm.create("pest.treatment", [{
            visit_id: this.state.selectedVisit.id,
        }]);
        this.state.treatment = {
            id: ids[0],
            pest_id: null,
            method_id: null,
            zone_id: null,
            result: "completed",
            notes: "",
        };
        this.state.treatmentProducts = await this.orm.searchRead(
            "product.product",
            [["detailed_type", "=", "consu"], ["active", "=", true]],
            ["id", "display_name", "uom_id"],
            { order: "display_name asc", limit: 200 }
        );
        this.state.stockLocations = await this.orm.searchRead(
            "stock.location",
            [
                ["usage", "=", "internal"],
                ["company_id", "in", [user.activeCompany?.id || false]],
            ],
            ["id", "display_name"],
            { order: "display_name asc", limit: 200 }
        );
        this.state.treatmentLots = [];
        this.state.treatmentLine = {
            product_id: null,
            lot_id: null,
            quantity: 1,
            location_id: null,
        };
        this.state.treatmentPhoto = null;
        this.state.view = "treatment";
    }

    async loadTreatmentLots(productId) {
        if (!productId) {
            this.state.treatmentLots = [];
            return;
        }
        this.state.treatmentLots = await this.orm.searchRead(
            "stock.lot",
            [["product_id", "=", productId]],
            ["id", "name", "expiration_date", "product_id"],
            { order: "expiration_date asc, name asc", limit: 200 }
        );
    }

    async onTreatmentProductChange(event) {
        const productId = Number(event.target.value) || null;
        this.state.treatmentLine.product_id = productId;
        this.state.treatmentLine.lot_id = null;
        await this.loadTreatmentLots(productId);
    }

    onTreatmentPhoto(event) {
        this.state.treatmentPhoto = event.target.files?.[0] || null;
    }

    async saveTreatment() {
        if (!this.state.treatment?.id) {
            return;
        }

        const treatmentVals = {
            pest_id: this.state.treatment.pest_id || false,
            method_id: this.state.treatment.method_id || false,
            zone_id: this.state.treatment.zone_id || false,
            result: this.state.treatment.result || "completed",
            notes: this.state.treatment.notes || false,
        };


        if (this.state.treatmentPhoto) {
            treatmentVals.image_1920 = await this.fileToBase64(this.state.treatmentPhoto);
        }

        await this.orm.write(
            "pest.treatment",
            [this.state.treatment.id],
            [treatmentVals]
        );

        if (this.state.treatmentLine.product_id) {
            await this.orm.create("pest.treatment.line", [{
                treatment_id: this.state.treatment.id,
                product_id: this.state.treatmentLine.product_id,
                lot_id: this.state.treatmentLine.lot_id || false,
                quantity: Number(this.state.treatmentLine.quantity) || 1,
                location_id: this.state.treatmentLine.location_id || false,
            }]);
        }

        if (this.state.treatmentPhoto) {
            const base64 = await this.fileToBase64(this.state.treatmentPhoto);
            await this.orm.create("ir.attachment", [{
                name: `treatment-${this.state.treatment.id}.jpg`,
                res_model: "pest.treatment",
                res_id: this.state.treatment.id,
                type: "binary",
                datas: base64,
                mimetype: this.state.treatmentPhoto.type || "image/jpeg",
            }]);
        }

        this.notifySuccess("Treatment saved.");
        this.state.view = "visit";
        await this.refreshSelectedVisit();
    }

    async consumeTreatment(treatmentId) {
        await this.orm.call(
            "pest.treatment",
            "action_consume_products",
            [[treatmentId]]
        );
        this.notifySuccess("Products consumed from stock.");
        await this.refreshSelectedVisit();
    }

    onInspectionField(lineId, field, value) {
        if (!this.state.inspectionLines[lineId]) {
            return;
        }
        this.state.inspectionLines[lineId][field] = value;
    }

    onInspectionHeaderField(field, value) {
        if (!this.state.inspection) {
            this.state.inspection = {};
        }
        this.state.inspection[field] = value;
    }

    onTreatmentField(field, value) {
        if (!this.state.treatment) {
            return;
        }
        this.state.treatment[field] = value;
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const data = String(reader.result || "");
                resolve(data.includes(",") ? data.split(",")[1] : data);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    async getCurrentLocation() {
        if (!navigator.geolocation) {
            this.notifyError("Geolocation is not supported by this device/browser.");
            return null;
        }
        return new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
                (position) => resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy || 0,
                }),
                () => {
                    this.notifyError("Unable to read your current location. Please allow GPS access.");
                    resolve(null);
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
            );
        });
    }

    enterSignature() {
        this.state.signatureData = this.state.selectedVisit?.customer_signature || null;
        this.state.signerName = this.state.selectedVisit?.customer_signature_name || "";
        this.state.signatureNote = this.state.selectedVisit?.customer_signature_note || "";
        this.state.view = "signature";
    }

    clearSignature() {
        this.state.signatureData = null;
        const canvas = document.querySelector(".pestops-signature-pad");
        if (canvas) {
            const context = canvas.getContext("2d");
            context.clearRect(0, 0, canvas.width, canvas.height);
        }
        this.state.mobileDraftSaved = false;
    }

    signatureStart(event) {
        const canvas = event.currentTarget;
        const rect = canvas.getBoundingClientRect();
        const context = canvas.getContext("2d");
        context.lineWidth = 2.2;
        context.lineCap = "round";
        context.lineJoin = "round";
        context.beginPath();
        context.moveTo(event.clientX - rect.left, event.clientY - rect.top);
        this._signatureDrawing = true;
        event.preventDefault();
    }

    signatureMove(event) {
        if (!this._signatureDrawing) {
            return;
        }
        const canvas = event.currentTarget;
        const rect = canvas.getBoundingClientRect();
        const context = canvas.getContext("2d");
        context.lineTo(event.clientX - rect.left, event.clientY - rect.top);
        context.stroke();
        event.preventDefault();
    }

    async signatureEnd(event) {
        if (!this._signatureDrawing) {
            return;
        }
        this._signatureDrawing = false;
        const canvas = event.currentTarget;
        this.state.signatureData = canvas.toDataURL("image/png").split(",")[1];
        this.state.mobileDraftSaved = false;
        await this.saveMobileDraft();
    }

    async saveMobileDraft() {
        const visitId = this.state.selectedVisit?.id;
        if (!visitId) {
            return;
        }
        const draft = {
            signature: this.state.signatureData || null,
            signerName: this.state.signerName || "",
            signatureNote: this.state.signatureNote || "",
            savedAt: new Date().toISOString(),
        };
        try {
            localStorage.setItem(`pestops-mobile-draft-${visitId}`, JSON.stringify(draft));
            this.state.mobileDraftSaved = true;
        } catch (error) {
            this.notifyInfo("The device could not store a local mobile draft.");
        }
    }

    restoreMobileDraft() {
        const visitId = this.state.selectedVisit?.id;
        if (!visitId) {
            return;
        }
        try {
            const raw = localStorage.getItem(`pestops-mobile-draft-${visitId}`);
            if (!raw) {
                this.state.mobileDraftSaved = false;
                return;
            }
            const draft = JSON.parse(raw);
            this.state.signatureData = draft.signature || this.state.selectedVisit.customer_signature || null;
            this.state.signerName = draft.signerName || this.state.selectedVisit.customer_signature_name || "";
            this.state.signatureNote = draft.signatureNote || this.state.selectedVisit.customer_signature_note || "";
            this.state.mobileDraftSaved = true;
        } catch (error) {
            this.state.mobileDraftSaved = false;
        }
    }

    clearMobileDraft() {
        const visitId = this.state.selectedVisit?.id;
        if (visitId) {
            localStorage.removeItem(`pestops-mobile-draft-${visitId}`);
        }
        this.state.mobileDraftSaved = false;
    }

    async completeMobileVisit() {
        if (!this.state.online) {
            await this.saveMobileDraft();
            this.notifyInfo("You are offline. The signature was saved locally; reconnect to complete the visit.");
            return;
        }
        const signatureRequired = false;
        if (signatureRequired && !this.state.signatureData) {
            this.notifyError("Customer signature is required.");
            return;
        }
        const location = await this.getCurrentLocation();
        if (!location) {
            return;
        }
        try {
            await this.orm.call(
                "pest.visit",
                "action_mobile_complete",
                [[this.state.selectedVisit.id], location.latitude, location.longitude, location.accuracy, this.state.signatureData || false, this.state.signerName || false, this.state.signatureNote || false]
            );
            this.clearMobileDraft();
            await this.refreshSelectedVisit();
            this.notifySuccess("Visit completed and customer acceptance recorded.");
        } catch (error) {
            this.notifyError(error?.data?.message || error?.message || "Unable to complete the visit.");
            throw error;
        }
    }

    async openBackendVisit() {
        if (!this.state.selectedVisit) {
            return;
        }
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "pest.visit",
            views: [[false, "form"]],
            res_id: this.state.selectedVisit.id,
            target: "current",
        });
    }
}

registry.category("actions").add(ACTION_TAG, PestOpsTechnicianApp);
