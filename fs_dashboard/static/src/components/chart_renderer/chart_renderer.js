/** @odoo-module **/

import { Component,useRef,onMounted } from "@odoo/owl";

export class ChartRenderer extends Component {
    setup(){
        this.chartRef = useRef("chart")
        onMounted(()=>this.renderChart())
    }

    renderChart(){
      let self = this
      let chart = new Chart(this.chartRef.el, {
              type: this.props.type,
              data: {
                labels: self.props.labels,
                datasets: [{
                  label:self.props.title,
                  data: self.props.datasets[0]['data'],
                  borderWidth: 1,},]
              },
              options: {
                maintainAspectRatio: false,
                responsiveAnimationDuration: 1000,
                animation: {easing: 'easeInQuad',},
                plugins:{
                    legend: { display: true ,
                              position:'top', 
                            
                    },
                    title: {
                      display: true,
                      text: self.props.title,
                    }
                },
                responsive: true,
               
                scales: {
                  y: {
                    beginAtZero: true
                  }
                },
              
              }
            }
        );
    
        self.__owl__.parent.component.charts.push(chart)
        return chart
    }
}

ChartRenderer.template = "ChartRenderer"