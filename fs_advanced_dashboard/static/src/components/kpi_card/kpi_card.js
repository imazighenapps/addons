/** @odoo-module **/


import { KpiCard } from '@fs_dashboard/components/kpi_card/kpi_card';
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(KpiCard.prototype,{
  
    setup() {
      super.setup();
      this.actionService = useService("action");
    },

    show_view(ev,domain,model,name){
        let self = this
        const action = {
                  name        : name,
                  type        : "ir.actions.act_window",
                  res_model   : model,
                  views       : [[false, "list"], [false, "form"]],
                  view_mode   : 'form',
                  domain      : domain,
                //   target      : "new",
                  context     : {create: false,edit: false}
              };
        self.actionService.doAction(action, { });       

       
    }
   


})
