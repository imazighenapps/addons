/** @odoo-module */

const { Component, useState, onWillUnmount, onWillDestroy, useRef, onMounted } = owl;
import { rpc } from "@web/core/network/rpc";

export class TuplesOut extends Component {
    setup() {
        this.chartRef = useRef("tuples-out");
        this.state = useState({ val: {} });
        onMounted(() => this.renderChart());
        this.intervalId = null;
        onWillDestroy(() => { clearInterval(this.intervalId); });
        onWillUnmount(() => { clearInterval(this.intervalId); });
    }

    renderChart() {
        let self = this;
        let data = {
            labels: Array(20).fill(""), // 60 labels pour les dernières 60 secondes
            datasets: [
                {
                    label: "Fetched",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',  // fond blanc pour différencier
                    borderColor: 'rgba(33, 150, 243, 1)',  // bleu différent
                    borderWidth: 2,
                },
                {
                    label: "Returned",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',  // fond blanc pour différencier
                    borderColor: 'rgba(255, 87, 34, 1)',  // orange différent
                    borderWidth: 2,
                }
            ]
        };

        let chart = new Chart(this.chartRef.el, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                tooltips: {
                    enabled: true,  // Activer les tooltips
                    mode: 'nearest', // Mode de tooltip
                    intersect: false,
                    callbacks: {
                        label: function(tooltipItem, data) {
                            let label = data.datasets[tooltipItem.datasetIndex].label || '';
                            let value = tooltipItem.yLabel || tooltipItem.raw;
                            if (value === undefined) {
                                value = '0';
                            }

                            return `${label}: ${value}`;  // Texte de la tooltip
                        },
                    },
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',  // Couleur de fond de la tooltip
                    titleFontSize: 14,
                    bodyFontSize: 12,
                    bodyFontColor: '#fff',
                    titleFontColor: '#fff',
                    bodySpacing: 4,
                    padding: 10,
                },
                legend: {
                    display: true,
                    position: 'top',
                },
                animation: { easing: 'easeInQuad' },
                plugins: {
                    title: { display: true, text: "Database Fetch/Return Statistics" }
                },
                elements: { point: { radius: 0 } },
                scales: {
                    y: { beginAtZero: true ,
                        ticks: {
                            autoSkip: true, // Pas d'une unité entre chaque tick
                            precision: 0, // Pas de décimales
                        }
                    },
                    x: { display: true,
                        ticks: {
                            autoSkip: true, // Pas d'une unité entre chaque tick
                            precision: 0, // Pas de décimales
                        }
                    }
                }
            }
        });

        self.update_data(chart);
        this.intervalId = setInterval(() => self.update_data(chart), 1000);
        return chart;
    }

    async update_data(chart) {
        let self = this;
        await rpc("/db/monitoring/query/tuples/out", {}).then(function(result) {
            if (Object.keys(self.state.val).length === 0) {
                self.state.val = result;  // Sauvegarder la première valeur
            } else {
                chart.data.datasets.forEach((dataset) => {
                    let datasetName = dataset.label;
                    let data = dataset.data;
                    let newValue;
                    switch (datasetName) {
                        case "Fetched":
                            newValue = result.fetched - self.state.val.fetched;
                            break;
                        case "Returned":
                            newValue = result.returned - self.state.val.returned;
                            break;
                        default:
                            newValue = 0;
                    }
                    if (data.length < 21) {
                        data.push(newValue);
                    } else {
                        data.shift();
                        data.push(newValue);
                    }

                    dataset.data = data;  // Appliquer les modifications
                });
                self.state.val = result;
            }

            chart.update("none");
        });
    }
}

TuplesOut.template = "TuplesOut";
