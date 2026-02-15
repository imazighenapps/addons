/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ForecastDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.chartRef = useRef("predictionChart");
        this.alertChartRef = useRef("alertChart");
        this.trendChartRef = useRef("trendChart");
        this.accuracyChartRef = useRef("accuracyChart");
        
        this.state = useState({
            kpis: {
                totalPredictions: 0,
                activeAlerts: 0,
                avgAccuracy: 0,
                estimatedSavings: 0,
                productsForecasted: 0,
                criticalAlerts: 0,
            },
            topProducts: [],
            recentAlerts: [],
            loading: true,
        });
        
        onWillStart(async () => {
            await this.loadData();
        });
        
        onMounted(() => {
            this.renderCharts();
        });
    }
    
    async loadData() {
        try {
            // Load KPIs
            const predictions = await this.orm.searchCount("forecast.prediction", [["active", "=", true]]);
            const alerts = await this.orm.searchCount("forecast.alert", [
                ["status", "in", ["new", "acknowledged"]]
            ]);
            const criticalAlerts = await this.orm.searchCount("forecast.alert", [
                ["severity", "=", "critical"],
                ["status", "in", ["new", "acknowledged"]]
            ]);
            
            // Get accuracy from predictions
            const accuracyData = await this.orm.searchRead(
                "forecast.prediction",
                [["accuracy_score", ">", 0]],
                ["accuracy_score"],
                { limit: 100 }
            );
            
            let avgAccuracy = 0;
            if (accuracyData.length > 0) {
                const sum = accuracyData.reduce((acc, pred) => acc + pred.accuracy_score, 0);
                avgAccuracy = sum / accuracyData.length;
            }
            
            // Get unique products with forecasts
            const productsData = await this.orm.call(
                "forecast.prediction",
                "read_group",
                [
                    [["active", "=", true]],
                    ["product_id"],
                    ["product_id"],
                ]
            );
            
            // Get top products by predicted demand
            const topProducts = await this.orm.searchRead(
                "forecast.prediction",
                [
                    ["date", ">=", new Date().toISOString().split('T')[0]],
                    ["date", "<=", this.getDatePlusDays(30)]
                ],
                ["product_id", "predicted_demand", "date", "trend"],
                { 
                    limit: 10,
                    order: "predicted_demand desc"
                }
            );
            
            // Get recent alerts
            const recentAlerts = await this.orm.searchRead(
                "forecast.alert",
                [["status", "in", ["new", "acknowledged"]]],
                ["product_id", "alert_type", "severity", "message", "date_detection"],
                { 
                    limit: 5,
                    order: "date_detection desc"
                }
            );
            
            // Update state
            this.state.kpis = {
                totalPredictions: predictions,
                activeAlerts: alerts,
                avgAccuracy: Math.round((100 - avgAccuracy) * 10) / 10, // Convert MAPE to accuracy %
                estimatedSavings: Math.round(predictions * 15.5), // Rough estimate
                productsForecasted: productsData.length,
                criticalAlerts: criticalAlerts,
            };
            
            this.state.topProducts = topProducts;
            this.state.recentAlerts = recentAlerts;
            this.state.loading = false;
            
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.loading = false;
        }
    }
    
    getDatePlusDays(days) {
        const date = new Date();
        date.setDate(date.getDate() + days);
        return date.toISOString().split('T')[0];
    }
    
    async renderCharts() {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded');
            return;
        }
        
        await this.renderPredictionChart();
        await this.renderAlertChart();
        await this.renderTrendChart();
        await this.renderAccuracyChart();
    }
    
    async renderPredictionChart() {
        if (!this.chartRef.el) return;
        
        // Get prediction data for next 30 days
        const predictions = await this.orm.searchRead(
            "forecast.prediction",
            [
                ["date", ">=", new Date().toISOString().split('T')[0]],
                ["date", "<=", this.getDatePlusDays(30)]
            ],
            ["date", "predicted_demand"],
            { order: "date asc", limit: 30 }
        );
        
        // Group by date
        const groupedData = {};
        predictions.forEach(pred => {
            if (!groupedData[pred.date]) {
                groupedData[pred.date] = 0;
            }
            groupedData[pred.date] += pred.predicted_demand;
        });
        
        const labels = Object.keys(groupedData).sort();
        const data = labels.map(date => Math.round(groupedData[date]));
        
        const ctx = this.chartRef.el.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.map(d => new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })),
                datasets: [{
                    label: 'Demande Prédite',
                    data: data,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Prévisions 30 Prochains Jours'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString('fr-FR');
                            }
                        }
                    }
                }
            }
        });
    }
    
    async renderAlertChart() {
        if (!this.alertChartRef.el) return;
        
        // Get alerts by type
        const alertsByType = await this.orm.call(
            "forecast.alert",
            "read_group",
            [
                [["status", "in", ["new", "acknowledged"]]],
                ["alert_type"],
                ["alert_type"],
            ]
        );
        
        const labels = [];
        const data = [];
        const colors = {
            'stockout': 'rgb(255, 99, 132)',
            'overstock': 'rgb(255, 159, 64)',
            'anomaly': 'rgb(255, 205, 86)',
            'trend': 'rgb(54, 162, 235)'
        };
        
        alertsByType.forEach(group => {
            const type = group.alert_type;
            labels.push(this.getAlertTypeLabel(type));
            data.push(group.alert_type_count);
        });
        
        const ctx = this.alertChartRef.el.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: Object.values(colors),
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: 'Alertes par Type'
                    }
                }
            }
        });
    }
    
    async renderTrendChart() {
        if (!this.trendChartRef.el) return;
        
        // Get trends
        const trends = await this.orm.call(
            "forecast.prediction",
            "read_group",
            [
                [["date", ">=", new Date().toISOString().split('T')[0]]],
                ["trend"],
                ["trend"],
            ]
        );
        
        const labels = [];
        const data = [];
        
        trends.forEach(group => {
            labels.push(this.getTrendLabel(group.trend));
            data.push(group.trend_count);
        });
        
        const ctx = this.trendChartRef.el.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Nombre de Produits',
                    data: data,
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(201, 203, 207, 0.8)'
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                    title: {
                        display: true,
                        text: 'Tendances de Demande'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    async renderAccuracyChart() {
        if (!this.accuracyChartRef.el) return;
        
        // Get accuracy over time (last 7 days of predictions that have actuals)
        const accuracyData = await this.orm.searchRead(
            "forecast.prediction",
            [
                ["accuracy_score", ">", 0],
                ["date", ">=", this.getDateMinusDays(7)],
                ["date", "<", new Date().toISOString().split('T')[0]]
            ],
            ["date", "accuracy_score"],
            { order: "date asc" }
        );
        
        // Group by date and average
        const groupedData = {};
        accuracyData.forEach(pred => {
            if (!groupedData[pred.date]) {
                groupedData[pred.date] = { sum: 0, count: 0 };
            }
            groupedData[pred.date].sum += pred.accuracy_score;
            groupedData[pred.date].count += 1;
        });
        
        const labels = Object.keys(groupedData).sort();
        const data = labels.map(date => {
            const avg = groupedData[date].sum / groupedData[date].count;
            return Math.round((100 - avg) * 10) / 10; // Convert MAPE to accuracy %
        });
        
        const ctx = this.accuracyChartRef.el.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.map(d => new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })),
                datasets: [{
                    label: 'Précision (%)',
                    data: data,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                    },
                    title: {
                        display: true,
                        text: 'Précision sur 7 Jours'
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    getDateMinusDays(days) {
        const date = new Date();
        date.setDate(date.getDate() - days);
        return date.toISOString().split('T')[0];
    }
    
    getAlertTypeLabel(type) {
        const labels = {
            'stockout': 'Rupture',
            'overstock': 'Surstock',
            'anomaly': 'Anomalie',
            'trend': 'Tendance'
        };
        return labels[type] || type;
    }
    
    getTrendLabel(trend) {
        const labels = {
            'increasing': 'Croissant',
            'decreasing': 'Décroissant',
            'stable': 'Stable'
        };
        return labels[trend] || trend;
    }
    
    getSeverityClass(severity) {
        const classes = {
            'critical': 'text-danger fw-bold',
            'high': 'text-danger',
            'medium': 'text-warning',
            'low': 'text-info'
        };
        return classes[severity] || '';
    }
    
    getSeverityLabel(severity) {
        const labels = {
            'critical': 'Critique',
            'high': 'Élevé',
            'medium': 'Moyen',
            'low': 'Bas'
        };
        return labels[severity] || severity;
    }
    
    async onRefresh() {
        this.state.loading = true;
        await this.loadData();
        await this.renderCharts();
    }
    
    async openPredictions() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'forecast.prediction',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }
    
    async openAlerts() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'forecast.alert',
            views: [[false, 'list'], [false, 'form']],
            domain: [['status', 'in', ['new', 'acknowledged']]],
            target: 'current',
        });
    }
    
    async openGenerateWizard() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'generate.forecast.wizard',
            views: [[false, 'form']],
            target: 'new',
        });
    }
}

ForecastDashboard.template = "im_ai_inventory_forecast.Dashboard";

registry.category("actions").add("forecast_dashboard", ForecastDashboard);