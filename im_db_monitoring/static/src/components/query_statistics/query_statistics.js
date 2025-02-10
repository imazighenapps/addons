/** @odoo-module */


const { Component,useState, onWillUnmount, onWillDestroy, useRef, onMounted } = owl;
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class QueryStatistics extends Component {
    setup() {
        this.chartRef = useRef("query-statistics");
        this.state = useState({ val:{}});
        onMounted(() => this.renderChart());
        this.intervalId = null;
        onWillDestroy(() => { clearInterval(this.intervalId); });
        onWillUnmount(() => { clearInterval(this.intervalId); });
    }

    renderChart() {
        let self = this;
        let data = {
            labels: Array(60).fill(""), // on garde 60 labels pour les dernières 60 secondes
            datasets: [
                {
                    label: "Commits",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(0, 128, 128, 1)',
                    borderWidth: 2,
                },
                {
                    label: "Rollbacks",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(200, 20, 50, 1)',
                    borderWidth: 1,
                },
                {
                    label: "Rows Read",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(102, 51, 153, 1)',
                    borderWidth: 2,
                },
                {
                    label: "Rows Modified",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(204, 97, 32, 1)',
                    borderWidth: 2,
                },
                {
                    label: "Blocks Accessed",
                    data: [],
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(204, 153, 51, 1)',
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
                  mode: 'nearest', // Le mode de la tooltip (ex: nearest pour point le plus proche)
                  intersect: false, // Si la tooltip doit apparaître seulement sur l'élément sélectionné ou également sur d'autres éléments de la ligne
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
                    title: { display: true, text: "Database Query Statistics" }
                },
                elements: { point: { radius: 0 } },
                scales: {
                    y: { beginAtZero: true ,
                      ticks: {
                        autoSkip: true, // force un pas d'une unité entre chaque tick
                        precision: 0, // évite les décimales
                    }
                    },
                    x: { display: true,
                      ticks: {
                        autoSkip: true, // force un pas d'une unité entre chaque tick
                        precision: 0, // évite les décimales
                    }
                     }
                }
            }
        });

        self.update_data(chart);
        this.intervalId = setInterval(() => self.update_data(chart), 1000);
        return chart;
    }

    async update_data(cpu_chart) {
      let self = this;
  
      await rpc("/db/monitoring/query/statistics", {}).then(function(result) {
          if (Object.keys(self.state.val).length === 0) {
              self.state.val = result;
          } else {
              cpu_chart.data.datasets.forEach((dataset) => {
                  let datasetName = dataset.label;
                  let data = dataset.data;
                  let newValue;
  
                  switch (datasetName) {
                      case "Commits":
                          newValue = result.total_commits - self.state.val.total_commits;
                          break;
                      case "Rollbacks":
                          newValue = result.total_rollbacks - self.state.val.total_rollbacks;
                          break;
                      case "Rows Read":
                          newValue = result.total_rows_read - self.state.val.total_rows_read;
                          break;
                      case "Rows Modified":
                          newValue = result.total_rows_modified - self.state.val.total_rows_modified;
                          break;
                      case "Blocks Accessed":
                          newValue = result.total_blocks_accessed - self.state.val.total_blocks_accessed;
                          break;
                      default:
                          newValue = 0;
                  }
  
                  if (data.length < 61) {
                      data.push(newValue);
                  } else {
                      data.shift();
                      data.push(newValue);
                  }
                  dataset.data = data;
              });
              self.state.val = result;
          }
          cpu_chart.update("none");
      });
  }
  
}

QueryStatistics.template = "QueryStatistics";
