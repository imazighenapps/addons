/** @odoo-module **/

import { registry } from "@web/core/registry"
import { KpiCard } from "./kpi_card/kpi_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets"
import { loadCSS } from "@web/core/assets";
import { Component, onWillStart, useRef, useState } from "@odoo/owl";

export class FsDashboard extends Component {
    setup(){
        this.dashMainRef = useRef("dashboard-main");
        this.rpc = useService("rpc");
        this.state = useState({ data:{}});
        this.charts = []

        onWillStart(async ()=>{
            let self = this
            await this.rpc("/get/data",{"dashboard_id" : this.props.action.params.dashboard_id,
                }).then(function (data) {
                    self.state.data = data
                });
                  
            const JSfiles = ["/fs_dashboard/static/src/lib/js/gridstack-h5.js","/fs_dashboard/static/src/lib/js/chart.js",];
            const CSSfiles = ["/fs_dashboard/static/src/lib/css/gridstack.min.css"];
            for (const file of JSfiles) {await loadJS(file);}
            for (const file of CSSfiles) {await loadCSS(file);}
            
           

      
        })
        
    }

   
}



FsDashboard.template = "Dashboard"
FsDashboard.components = { KpiCard,ChartRenderer}

registry.category("actions").add("dashboard_show", FsDashboard)