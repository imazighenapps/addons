/** @odoo-module */

const { Component, useState, onWillUnmount, onWillDestroy, useRef, onMounted } = owl;
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class BlockIo extends Component {
    setup() {
        this.chartRef = useRef("block-io");
        this.state = useState({ val: {} });
        onMounted(() => this.renderChart());
        this.intervalId = null;
        onWillDestroy(() => { clearInterval(this.intervalId); });
        onWillUnmount(() => { clearInterval(this.intervalId); });
    }

    renderChart() {
        let self = this;
        let data = {
            labels: Array(20).fill(""), // 20 labels pour les dernières secondes
            datasets: [
                {
                    label: "Reads",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',  // fond blanc pour différencier
                    borderColor: 'rgba(255, 99, 132, 1)',  // couleur rose pour les reads
                    borderWidth: 2,
                },
                {
                    label: "Hits",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',  // fond blanc pour différencier
                    borderColor: 'rgba(54, 162, 235, 1)',  // couleur bleue pour les hits
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
                    mode: 'nearest',
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
                    title: { display: true, text: "Block I/O Statistics (Reads & Hits)" }
                },
                elements: { point: { radius: 0 } },
                scales: {
                    y: { 
                        beginAtZero: true,
                        ticks: {
                            autoSkip: true, // Pas d'une unité entre chaque tick
                            precision: 0, // Pas de décimales
                        }
                    },
                    x: { 
                        display: true,
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
        await rpc("/db/monitoring/query/block/io", {}).then(function(result) {
            if (Object.keys(self.state.val).length === 0) {
                self.state.val = result;  // Sauvegarder la première valeur
            } else {
                chart.data.datasets.forEach((dataset) => {
                    let datasetName = dataset.label;
                    let data = dataset.data;
                    let newValue;
                    switch (datasetName) {
                        case "Reads":
                            newValue = result.reads - self.state.val.reads;
                            break;
                        case "Hits":
                            newValue = result.hits - self.state.val.hits;
                            break;
                        default:
                            newValue = 0;
                    }
                    // Ajouter la nouvelle valeur au dataset
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

            chart.update("none"); // Mettre à jour le graphique avec les nouvelles données
        });
    }
}

BlockIo.template = "BlockIo";
