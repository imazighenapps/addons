/** @odoo-module **/
// https://github.com/gridstack/gridstack.js#basic-usage
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { loadCSS } from "@web/core/assets";
import { qweb } from 'web.core';

const { Component, onWillStart,useRef,onPatched,onMounted } = owl;

class FsDashboard extends Component {
    
    setup() {
      this.rpc = useService("rpc");
      this.orm = useService('orm');
      async function loadJsFiles() {
        const files = ["/fs_dashboard/static/src/lib/js/gridstack-h5.js","/fs_dashboard/static/src/lib/js/chart.js",];
        for (const file of files) {await loadJS(file);}
        }

        async function loadCssFiles() {
            await Promise.all([
                  "/fs_dashboard/static/src/lib/css/gridstack.min.css"
                ].map((file) => loadCSS(file))
            );
        }

    onWillStart(() => Promise.all([loadJsFiles(), loadCssFiles()]));
        onMounted(() => {   
          console.log('onMounted');
          var self=this; 
          var grid;
    
          this.rpc("/get/data",{"dashboard_id" : this.props.action.params.dashboard_id,
              }).then(function (data) {
                  console.log('data=>',data);
                  grid = self.init_grid();
                  self.add_dashboard_tiles(grid,data['tiles']);
                  self.add_dashboard_sharts(grid,data['sharts']);

                 
              });
          
         });
    }

    init_grid(){
        var $gridstackContainer = $('.grid-stack');
        var grid = GridStack.init({
            staticGrid:true,
            float: true,
            cellHeight: 70,
            styleInHead : true,
            disableOneColumnMode: true,
        },$gridstackContainer[0]);
        return grid
        
    };

    add_dashboard_tiles(grid,tiles_data){
      for (let i = 0; i < tiles_data.length; i++){
          var $tile = $(qweb.render("fs_dashboard.tile",tiles_data[i]));
         

          $tile.find("#update_item").attr("t-on-click","updateItem");
          $tile.attr("id",tiles_data[i]['id']);

          grid.addWidget({w:3,h:2, content: $tile.prop('outerHTML')}) 

      }
    }

    add_dashboard_sharts(grid,shart_data){
      var self = this;
      console.log('shart_data=>',shart_data);
      for (let i = 0; i < shart_data.length; i++){
        var $chart = $(qweb.render("fs_dashboard.chart_view",[]));
        $chart.attr("id",shart_data[i]['id']);
        grid.addWidget({w:6,h:4, content: $chart.prop('outerHTML')})  
        const ctx = $('#'+shart_data[i]['id']);
        var values = shart_data[i]['data']['datasets'][0]['data'];
        new Chart(ctx, {
                        type: shart_data[i]['type'],
                        data: {
                          labels: shart_data[i]['data']['labels'],
                          datasets: [{
                            label: shart_data[i]['data']['datasets'][0]['label'],
                            data: values,
                            borderWidth: 1
                          }]
                        },
                        options: {
                          backgroundColor: "#000",
                          maintainAspectRatio: false,
                          responsiveAnimationDuration: 1000,
                          animation: {
                              easing: 'easeInQuad',
                          },

                          legend: { display: true },
                          responsive: true,
                          scales: {
                            y: {
                              beginAtZero: true
                            }
                          },
                         
                        }
                      }
                  );

        }

    }

    NumFormatter(num) {
        var digits = 1;
        var si = [{value: 1, symbol: ""}, {value: 1E3, symbol: "k"}, {value: 1E6, symbol: "M"}, {value: 1E9, symbol: "G"}, {value: 1E12, symbol: "T"}, {value: 1E15, symbol: "P"}, {value: 1E18, symbol: "E"}];
        return (num < 0 ? "-" : "") + (si.find(function(val) { return num < val.value; }).value / num).toFixed(digits).replace(/\.0+$|(\.[0-9]*[1-9])0+$/, "$1") + si.find(function(val) { return num < val.value; }).symbol;
    }

    updateItem() {
     console.log('****************');
  }  


}

FsDashboard.template = 'fs_dashboard.Dashboard';

registry.category('actions').add('dashboard_show', FsDashboard);

export default FsDashboard;
