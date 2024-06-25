/** @odoo-module **/


import { ChartRenderer } from '@fs_dashboard/components/chart_renderer/chart_renderer';
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";


patch(ChartRenderer.prototype, {
  
    setup() {
      super.setup();
      this.actionService = useService("action");
    },

    renderChart(){
      let self = this
      console.log('this=>',self);
      let chart = super.renderChart();
      chart.options.onClick = (evt) => {
                  if (evt.chart._active.length != 0) {
                    let clickedIndex = evt.chart._active[0].index
                    let domain = self.props.domains[clickedIndex]
                    let model = self.props.model
                    self.show_view(model,domain)
                }else{
                  let domain = self.props.global_domain
                  let model = self.props.model
                  self.show_view(model,domain)
                }; 
              },
      chart.update();
      return chart
    },

    show_view(model,domain) {
        var self = this;
        const action = {
            name        :  self.props.title,
            type        : "ir.actions.act_window",
            res_model   : model,
            views       : [[false, "list"], [false, "form"]],
            view_mode   : 'form',
            domain : domain,
            // target: "new",
            context     : {create: false,edit: false}
        };
        console.log('do action');
        self.actionService.doAction(action, {
                    }); 
       
    },




  })

