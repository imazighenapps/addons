/** @odoo-module */

const { Component, onWillUnmount,onWillDestroy, useRef,useState, onMounted } = owl
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class TableSizes extends Component {
    setup(){

   
        this.state = useState({ val:[]});
        onMounted(()=>this.renderTable())
        this.intervalId = setInterval(() => {
            this.renderTable();  
        }, 60000);
      
        onWillDestroy(() => {clearInterval(this.intervalId);});
        onWillUnmount(() => {clearInterval(this.intervalId);});
    }

    async renderTable(){
        let self=this
        await rpc("/db/monitoring/table/sizes",{
        }).then(function(result){
           
            self.state.val = result
            console.log("self.state.val0=>",self.state.val[0])
            console.log("self.state.val=>",self.state.val)
        })   

    }


}

TableSizes.template = "TableSizes"