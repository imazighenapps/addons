/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { DbStatus } from "./db_status/db_status"
import { QueryStatistics } from "./query_statistics/query_statistics"
import { TuplesIn } from "./tuples_in/tuples_in"
import { TuplesOut } from "./tuples_out/tuples_out"
import { BlockIo } from "./block_io/block_io"
import { TableSizes } from "./table_sizes/table_sizes"


const { Component, onWillStart, onMounted, useRef, useState } = owl;


export class DbMonitoring extends Component {

    setup() {
      
        onWillStart(async () => {
            let self = this;
            const JSfiles = ["/web/static/lib/Chart/Chart.js"];
            for (const file of JSfiles) { await loadJS(file); }
         
        });
      
    }

}


DbMonitoring.components = {DbStatus,QueryStatistics,TuplesIn,TuplesOut,BlockIo,TableSizes}

DbMonitoring.template = "DbMonitoring";
registry.category("actions").add("db_monitoring", DbMonitoring);
