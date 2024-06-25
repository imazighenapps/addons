/** @odoo-module **/


import { FsDashboard } from '@fs_dashboard/components/main';
import { patch } from "@web/core/utils/patch";
import { onWillDestroy } from "@odoo/owl";

patch(FsDashboard.prototype,{
    setup() {
        super.setup();
        let self = this;
        let do_refresh_fnc = setInterval(() => {self.do_refresh()}, "60000");
        onWillDestroy(() => {clearInterval(do_refresh_fnc);});
    },
   
    async do_filter(ev){
        let period
        if (ev){
            period = ev.target.value
        }else{
            period = $(".form-select" ).val()
        }  
        let self = this
        await this.rpc("/do/filter/data",{"period" : period, data: self.state.data
            }).then(function (data) {              
                self.state.data = data
                for (let i = 0; i < self.charts.length; i++) {
                    self.charts[i].data = data['sharts'][i].data
                    self.charts[i].update("none")
                  }
            });
    },

    async do_refresh(){
        this.do_filter()
    },


})