/** @odoo-module **/

import {
    Component,
    onWillStart,
    onMounted,
    onWillUnmount,
    onPatched,
    useRef,
    useState,
} from "@odoo/owl";

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { loadJS } from "@web/core/assets";

// IMPORTANT : Chart.js n'est pas bundlé par défaut sur cette action.
// On le charge explicitement via loadJS() avant le premier rendu,
// puis on utilise la variable globale `Chart` qu'il expose.

// ============================================================================
// FORMATTERS
// ============================================================================

const FMT = {
    amount(value) {
        const n = Number.parseFloat(value) || 0;

        if (n >= 1e9) {
            return (n / 1e9).toFixed(2) + " Mrd";
        }

        if (n >= 1e6) {
            return (n / 1e6).toFixed(2) + " M";
        }

        if (n >= 1e3) {
            return (n / 1e3).toFixed(1) + " K";
        }

        return Math.round(n).toLocaleString();
    },

    pct(value) {
        return (Number.parseFloat(value) || 0).toFixed(1) + "%";
    },

    number(value) {
        return (Number.parseFloat(value) || 0).toLocaleString();
    },
};

// ============================================================================
// COLORS
// ============================================================================

const COLORS = {
    blue: "#5e8fff",
    green: "#26de81",
    orange: "#fd9644",
    purple: "#a55eea",
    cyan: "#4ecdc4",
    yellow: "#f6c90e",
    red: "#fc5c65",
    grey: "#8899bb",
    dark: "#343a40",
    white: "#ffffff",
};

// ============================================================================
// HELPERS
// ============================================================================

function toNumber(value) {
    const number = Number.parseFloat(value);

    return Number.isFinite(number) ? number : 0;
}

function toInteger(value) {
    return Math.round(toNumber(value));
}

function safeArray(value) {
    return Array.isArray(value) ? value : [];
}

function safeObject(value) {
    return value && typeof value === "object" ? value : {};
}

// ============================================================================
// DASHBOARD
// ============================================================================

export class DashboardEducation extends Component {
    static template = "eduflow.DashboardEducation";

    setup() {
        // --------------------------------------------------------------------
        // Services
        // --------------------------------------------------------------------

        this.notification = useService("notification");

        // --------------------------------------------------------------------
        // State
        // --------------------------------------------------------------------

        this.state = useState({
            loading: true,
            data: {},
        });

        // --------------------------------------------------------------------
        // OWL refs
        // --------------------------------------------------------------------

        this.enrollmentCanvas = useRef("enrollmentCanvas");
        this.feesCanvas = useRef("feesCanvas");
        this.genderCanvas = useRef("genderCanvas");
        this.admissionsCanvas = useRef("admissionsCanvas");
        this.classroomCanvas = useRef("classroomCanvas");
        this.teachersCanvas = useRef("teachersCanvas");
        this.examsCanvas = useRef("examsCanvas");
        this.topClassesCanvas = useRef("topClassesCanvas");

        // --------------------------------------------------------------------
        // Charts
        // --------------------------------------------------------------------

        this.charts = {};

        // Empêche plusieurs render simultanés
        this._chartsScheduled = false;

        // --------------------------------------------------------------------
        // Lifecycle
        // --------------------------------------------------------------------

        onWillStart(async () => {
            // Charge la librairie Chart.js une seule fois, avant que le
            // composant ne tente de créer le moindre graphique.
            await loadJS("/web/static/lib/Chart/Chart.js");
        });

        onMounted(async () => {
            console.log(
                "[DashboardEducation] Component mounted"
            );

            await this._loadData();
        });

        /*
         * IMPORTANT :
         *
         * Après state.data = data, OWL doit d'abord reconstruire le DOM.
         *
         * onPatched() est donc l'endroit idéal pour attendre que les canvas
         * existent réellement.
         */
        onPatched(() => {
            if (!this.state.loading) {
                this._scheduleChartsRender();
            }
        });

        onWillUnmount(() => {
            console.log(
                "[DashboardEducation] Component unmounted"
            );

            this._destroyAllCharts();
        });
    }

    // ========================================================================
    // GETTERS
    // ========================================================================

    get kpi() {
        return this.state.data || {};
    }

    // ========================================================================
    // LOAD DATA
    // ========================================================================

    async _loadData() {
        console.log(
            "[DashboardEducation] Loading dashboard data..."
        );

        this.state.loading = true;

        try {
            const data = await rpc(
                "/dashboard/education/data",
                {}
            );

            console.log(
                "[DashboardEducation] Data received:",
                data
            );

            this.state.data = data || {};

        } catch (error) {
            console.error(
                "[DashboardEducation] Error loading data:",
                error
            );

            this.notification.add(
                "Erreur lors du chargement du dashboard.",
                {
                    type: "danger",
                }
            );

            this.state.data = {};

        } finally {
            this.state.loading = false;
        }
    }

    // ========================================================================
    // REFRESH
    // ========================================================================

    async refresh() {
        await this._loadData();
    }

    // ========================================================================
    // CHART SCHEDULER
    // ========================================================================

    _scheduleChartsRender() {
        if (this._chartsScheduled) {
            return;
        }

        this._chartsScheduled = true;

        /*
         * requestAnimationFrame permet de laisser le navigateur terminer
         * la mise à jour du DOM effectuée par OWL.
         */
        requestAnimationFrame(() => {
            this._chartsScheduled = false;

            if (this.isDestroyed) {
                return;
            }

            this._renderCharts();
        });
    }

    // ========================================================================
    // CANVAS
    // ========================================================================

    _getCanvas(ref, name) {
        if (!ref || !ref.el) {
            console.warn(
                `[DashboardEducation] Canvas "${name}" introuvable.`
            );

            return null;
        }

        return ref.el;
    }

    // ========================================================================
    // CREATE CHART
    // ========================================================================

    _createChart(key, ref, config) {
        if (typeof Chart === "undefined") {
            console.error(
                `[DashboardEducation] Chart.js n'est pas chargé, impossible de créer "${key}".`
            );

            return;
        }

        const canvas = this._getCanvas(ref, key);

        if (!canvas) {
            return;
        }

        // Détruire l'ancien graphique
        this._destroyChart(key);

        const context = canvas.getContext("2d");

        if (!context) {
            console.error(
                `[DashboardEducation] Context 2D indisponible pour "${key}".`
            );

            return;
        }

        try {
            this.charts[key] = new Chart(
                context,
                config
            );

            console.log(
                `[DashboardEducation] Chart "${key}" créé.`
            );

        } catch (error) {
            console.error(
                `[DashboardEducation] Erreur création "${key}":`,
                error
            );
        }
    }

    // ========================================================================
    // DESTROY CHART
    // ========================================================================

    _destroyChart(key) {
        const chart = this.charts[key];

        if (!chart) {
            return;
        }

        try {
            chart.destroy();
        } catch (error) {
            console.warn(
                `[DashboardEducation] Erreur destruction "${key}":`,
                error
            );
        }

        delete this.charts[key];
    }

    // ========================================================================
    // DESTROY ALL
    // ========================================================================

    _destroyAllCharts() {
        Object.keys(this.charts).forEach((key) => {
            this._destroyChart(key);
        });
    }

    // ========================================================================
    // COMMON OPTIONS
    // ========================================================================

    _commonOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,

            animation: {
                duration: 400,
            },

            plugins: {
                legend: {
                    display: false,
                },
            },
        };
    }

    // ========================================================================
    // RENDER ALL CHARTS
    // ========================================================================

    _renderCharts() {
        const data = this.state.data || {};

        console.log(
            "[DashboardEducation] Rendering charts..."
        );

        this._renderEnrollmentChart(data);

        this._renderFeesChart(data);

        this._renderGenderChart(data);

        this._renderAdmissionsChart(data);

        this._renderClassroomChart(data);

        this._renderTeachersChart(data);

        this._renderExamsChart(data);

        this._renderTopClassesChart(data);
    }

    // ========================================================================
    // 1 - ENROLLMENT BY LEVEL
    // ========================================================================

    _renderEnrollmentChart(data) {
        const rows = safeArray(
            data.by_level
        );

        const labels = rows.map(
            (item) => item.level || "Unknown"
        );

        const values = rows.map(
            (item) => toInteger(item.count)
        );

        this._createChart(
            "chart_enrollment_level",
            this.enrollmentCanvas,
            {
                type: "bar",

                data: {
                    labels,

                    datasets: [
                        {
                            label: "Students",

                            data: values,

                            backgroundColor: COLORS.blue,

                            borderColor: COLORS.blue,

                            borderWidth: 1,

                            borderRadius: 6,

                            maxBarThickness: 50,
                        },
                    ],
                },

                options: {
                    ...this._commonOptions(),

                    scales: {
                        y: {
                            beginAtZero: true,

                            ticks: {
                                precision: 0,
                            },
                        },
                    },
                },
            }
        );
    }

    // ========================================================================
    // 2 - FEES BY MONTH
    // ========================================================================

    _renderFeesChart(data) {
        const rows = safeArray(
            data.fees_by_month
        );

        const labels = rows.map(
            (item) => item.month || ""
        );

        const invoiced = rows.map(
            (item) => toNumber(item.invoiced)
        );

        const collected = rows.map(
            (item) => toNumber(item.collected)
        );

        this._createChart(
            "chart_fees_month",
            this.feesCanvas,
            {
                type: "line",

                data: {
                    labels,

                    datasets: [
                        {
                            label: "Invoiced",

                            data: invoiced,

                            borderColor: COLORS.yellow,

                            backgroundColor:
                                "rgba(246, 201, 14, 0.15)",

                            borderWidth: 2,

                            tension: 0.4,

                            fill: true,

                            pointRadius: 3,

                            pointHoverRadius: 5,
                        },

                        {
                            label: "Collected",

                            data: collected,

                            borderColor: COLORS.green,

                            backgroundColor:
                                "rgba(38, 222, 129, 0.10)",

                            borderWidth: 2,

                            tension: 0.4,

                            fill: false,

                            pointRadius: 3,

                            pointHoverRadius: 5,
                        },
                    ],
                },

                options: {
                    ...this._commonOptions(),

                    interaction: {
                        mode: "index",
                        intersect: false,
                    },

                    plugins: {
                        legend: {
                            display: true,
                            position: "bottom",
                        },
                    },

                    scales: {
                        y: {
                            beginAtZero: true,
                        },
                    },
                },
            }
        );
    }

    // ========================================================================
    // 3 - STUDENTS BY GENDER
    // ========================================================================

    _renderGenderChart(data) {
        const students = safeObject(
            data.students
        );

        const rows = safeArray(
            students.by_gender
        );

        const labels = rows.map(
            (item) => item.label || "Unknown"
        );

        const values = rows.map(
            (item) => toInteger(item.count)
        );

        this._createChart(
            "chart_students_gender",
            this.genderCanvas,
            {
                type: "doughnut",

                data: {
                    labels,

                    datasets: [
                        {
                            data: values,

                            backgroundColor: [
                                COLORS.blue,
                                COLORS.orange,
                                COLORS.purple,
                                COLORS.cyan,
                            ],

                            borderColor: COLORS.white,

                            borderWidth: 2,
                        },
                    ],
                },

                options: {
                    responsive: true,

                    maintainAspectRatio: false,

                    cutout: "65%",

                    plugins: {
                        legend: {
                            display: true,
                            position: "bottom",
                        },
                    },
                },
            }
        );
    }

    // ========================================================================
    // 4 - ADMISSIONS
    // ========================================================================

    _renderAdmissionsChart(data) {
        const admissions = safeObject(
            data.admissions
        );

        const values = [
            toInteger(admissions.new),
            toInteger(admissions.review),
            toInteger(admissions.interview),
            toInteger(admissions.accepted),
            toInteger(admissions.refused),
        ];

        this._createChart(
            "chart_admissions_state",
            this.admissionsCanvas,
            {
                type: "bar",

                data: {
                    labels: [
                        "New",
                        "Review",
                        "Interview",
                        "Accepted",
                        "Refused",
                    ],

                    datasets: [
                        {
                            label: "Admissions",

                            data: values,

                            backgroundColor: [
                                COLORS.yellow,
                                COLORS.blue,
                                COLORS.purple,
                                COLORS.green,
                                COLORS.red,
                            ],

                            borderRadius: 5,

                            maxBarThickness: 50,
                        },
                    ],
                },

                options: {
                    ...this._commonOptions(),

                    scales: {
                        y: {
                            beginAtZero: true,

                            ticks: {
                                precision: 0,
                            },
                        },
                    },
                },
            }
        );
    }

    // ========================================================================
    // 5 - CLASSROOM OCCUPANCY
    // ========================================================================

    _renderClassroomChart(data) {
        const rows = safeArray(
            data.classrooms
        ).slice(0, 8);

        const labels = rows.map(
            (item) => item.name || "Unknown"
        );

        const values = rows.map((item) => {
            const value = toNumber(item.rate);

            return Math.max(
                0,
                Math.min(100, value)
            );
        });

        this._createChart(
            "chart_classroom_occupancy",
            this.classroomCanvas,
            {
                type: "bar",

                data: {
                    labels,

                    datasets: [
                        {
                            label: "Occupancy %",

                            data: values,

                            backgroundColor: COLORS.cyan,

                            borderColor: COLORS.cyan,

                            borderRadius: 5,

                            maxBarThickness: 30,
                        },
                    ],
                },

                options: {
                    ...this._commonOptions(),

                    indexAxis: "y",

                    scales: {
                        x: {
                            beginAtZero: true,

                            max: 100,

                            ticks: {
                                callback(value) {
                                    return value + "%";
                                },
                            },
                        },
                    },

                    plugins: {
                        legend: {
                            display: false,
                        },

                        tooltip: {
                            callbacks: {
                                label(context) {
                                    return (
                                        "Occupancy: " +
                                        toNumber(
                                            context.raw
                                        ).toFixed(1) +
                                        "%"
                                    );
                                },
                            },
                        },
                    },
                },
            }
        );
    }

    // ========================================================================
    // 6 - TEACHERS BY SPECIALTY
    // ========================================================================

    _renderTeachersChart(data) {
        const teachers = safeObject(
            data.teachers
        );

        const rows = safeArray(
            teachers.by_specialty
        );

        const labels = rows.map(
            (item) =>
                item.specialty || "Unknown"
        );

        const values = rows.map(
            (item) => toInteger(item.count)
        );

        this._createChart(
            "chart_teachers_specialty",
            this.teachersCanvas,
            {
                type: "pie",

                data: {
                    labels,

                    datasets: [
                        {
                            data: values,

                            backgroundColor: [
                                COLORS.blue,
                                COLORS.green,
                                COLORS.orange,
                                COLORS.purple,
                                COLORS.cyan,
                                COLORS.yellow,
                                COLORS.red,
                                COLORS.grey,
                            ],

                            borderColor: COLORS.white,

                            borderWidth: 2,
                        },
                    ],
                },

                options: {
                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            display: true,
                            position: "bottom",
                        },
                    },
                },
            }
        );
    }

    // ========================================================================
    // 7 - EXAMS BY STATE
    // ========================================================================

    _renderExamsChart(data) {
        const exams = safeObject(
            data.exams
        );

        const rows = safeArray(
            exams.by_state
        );

        const labels = rows.map(
            (item) => item.label || "Unknown"
        );

        const values = rows.map(
            (item) => toInteger(item.count)
        );

        this._createChart(
            "chart_exams_state",
            this.examsCanvas,
            {
                type: "doughnut",

                data: {
                    labels,

                    datasets: [
                        {
                            data: values,

                            backgroundColor: [
                                COLORS.grey,
                                COLORS.yellow,
                                COLORS.green,
                                COLORS.blue,
                                COLORS.red,
                            ],

                            borderColor: COLORS.white,

                            borderWidth: 2,
                        },
                    ],
                },

                options: {
                    responsive: true,

                    maintainAspectRatio: false,

                    cutout: "60%",

                    plugins: {
                        legend: {
                            display: true,
                            position: "bottom",
                        },
                    },
                },
            }
        );
    }

    // ========================================================================
    // 8 - TOP CLASSES
    // ========================================================================

    _renderTopClassesChart(data) {
        const grades = safeObject(
            data.grades
        );

        const rows = safeArray(
            grades.top_classes
        ).slice(0, 10);

        const labels = rows.map(
            (item) => item.name || "Unknown"
        );

        const values = rows.map((item) => {
            const value = toNumber(item.avg);

            return Math.max(
                0,
                Math.min(20, value)
            );
        });

        this._createChart(
            "chart_top_classes",
            this.topClassesCanvas,
            {
                type: "bar",

                data: {
                    labels,

                    datasets: [
                        {
                            label: "Average /20",

                            data: values,

                            backgroundColor: COLORS.purple,

                            borderColor: COLORS.purple,

                            borderRadius: 5,

                            maxBarThickness: 40,
                        },
                    ],
                },

                options: {
                    ...this._commonOptions(),

                    scales: {
                        y: {
                            beginAtZero: true,

                            max: 20,

                            ticks: {
                                callback(value) {
                                    return value + "/20";
                                },
                            },
                        },
                    },

                    plugins: {
                        legend: {
                            display: false,
                        },

                        tooltip: {
                            callbacks: {
                                label(context) {
                                    return (
                                        "Average: " +
                                        toNumber(
                                            context.raw
                                        ).toFixed(2) +
                                        "/20"
                                    );
                                },
                            },
                        },
                    },
                },
            }
        );
    }
}

// ============================================================================
// REGISTRY
// ============================================================================

registry.category("actions").add(
    "eduflow_dashboard_education",
    DashboardEducation
);
