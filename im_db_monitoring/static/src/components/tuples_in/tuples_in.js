/** @odoo-module */

const { Component, useState, onWillUnmount, onWillDestroy, useRef, onMounted } = owl;
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
export class TuplesIn extends Component {
    setup() {
        this.chartRef = useRef("tuples-in");
        this.state = useState({ val: {} });
        onMounted(() => this.renderChart());
        this.intervalId = null;
        onWillDestroy(() => { clearInterval(this.intervalId); });
        onWillUnmount(() => { clearInterval(this.intervalId); });
    }

    renderChart() {
        let self = this;
        let data = {
            labels: Array(20).fill(""), // on garde 20 labels pour les dernières 60 secondes
            datasets: [
                {
                    label: "Inserts",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(0, 128, 128, 1)',
                    borderWidth: 2,
                },
                {
                    label: "Updates",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(200, 20, 50, 1)',
                    borderWidth: 1,
                },
                {
                    label: "Deletes",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(102, 51, 153, 1)',
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
                    enabled: true,  
                    mode: 'nearest',  
                    intersect: false, 
                    callbacks: {
                        label: function(tooltipItem, data) {
                            let label = data.datasets[tooltipItem.datasetIndex].label || '';
                            let value = tooltipItem.yLabel || tooltipItem.raw;
                            if (value === undefined) {
                                value = '0';
                            }

                            return `${label}: ${value}`; 
                        },
                    },
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',  
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
                    title: { display: true, text: "Database Operations (Inserts, Updates, Deletes)" }
                },
                elements: { point: { radius: 0 } },
                scales: {
                    y: { beginAtZero: true ,
                        ticks: {
                            autoSkip: true, 
                            precision: 0, 
                        }
                    },
                    x: { display: true,
                        ticks: {
                            autoSkip: true, 
                            precision: 0, 
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

        await rpc("/db/monitoring/query/tuples/in", {}).then(function(result) {
            if (Object.keys(self.state.val).length === 0) {
                self.state.val = result;  // Sauvegarder la première valeur
            } else {
                chart.data.datasets.forEach((dataset) => {
                    let datasetName = dataset.label;
                    let data = dataset.data;
                    let newValue;
                    switch (datasetName) {
                        case "Inserts":
                            newValue = result.inserts - self.state.val.inserts;
                            break;
                        case "Updates":
                            newValue = result.updates - self.state.val.updates;
                            break;
                        case "Deletes":
                            newValue = result.deletes - self.state.val.deletes;
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
                    dataset.data = data;  
                });
                
                self.state.val = result;
            }

            chart.update("none");
        });
    }
}

TuplesIn.template = "TuplesIn";
