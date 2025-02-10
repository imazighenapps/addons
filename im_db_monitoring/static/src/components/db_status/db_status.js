/** @odoo-module */

const { Component,onWillUnmount, onWillDestroy,useRef, onMounted,useState } = owl
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
export class DbStatus extends Component {
    setup(){
        let self = this

        this.state = useState({ val:{}});
        this.chartRef = useRef("ram_chart")
        onMounted(()=>this.GetDbStatus())
    }

    async GetDbStatus(){
      let self=this;
      await rpc("/db/monitoring/general/status",{
        }).then(function(result){
            self.state.val = result

        })    


    }





}

DbStatus.template = "DbStatus"