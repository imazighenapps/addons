odoo.define('im_server_monitoring.server_monitoring_client', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var QWeb = core.qweb;

    var x=14;
    var ServerMonitoring = AbstractAction.extend({
        events: {
         

        },
        /**
         * @override
         */

         jsLibs: [
            '/web/static/lib/Chart/Chart.js',
            ],
            cssLibs: [
              
            ],
      
        init: function(parent, context) {           
            this._super(parent, context);
            var self = this;
        

        },
        willStart: function() {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function() {
            var self = this;
            self.render();
           
        },

        update_cpu_data:function(cpu_shart){
            var self = this;
            ajax.jsonRpc('/server/monitoring/cpu/informations', 'call', 
            {
            }).then(function(result){
                if ( cpu_shart.data.labels.length < 17){
                    cpu_shart.data.labels.push(result.current_seconds)
                }else{
                    cpu_shart.data.labels.shift();
                    cpu_shart.data.labels.push(result.current_seconds)
                }
                cpu_shart.data.datasets.forEach((dataset) => {
                    if (dataset.data.length < 17){
                        dataset.data.push(result.cpu_percent);
                    }
                    else{
                        dataset.data.shift();
                        dataset.data.push(result.cpu_percent);
                    }
                });
                $("#cpu_usage_info").text(result.cpu_percent.toString()+'%');
                cpu_shart.update();
            })
        },

        do_cpu_chart: function(){
            var self = this;
            var ctx = self.$el.find('#cpu_usage');
            var cpu_shart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: ['rgba(16, 167, 254, 0.1)'],
                        borderColor: ['rgba(16, 167, 254, 1)'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    layout: {padding: {left: 0, right: 20, top: 5, bottom: 20}},
                    legend: {display: false,},
                    tooltips: {
                        enabled: false
                    },
                    scales: {
                        yAxes: [{ticks: {display: false ,beginAtZero: true,steps: 1,stepValue: 1,max: 100}}],
                        xAxes: [{ticks: {display: true}}]
                    },
                    elements: {
                        point:{
                            radius: 0
                        }
                    },
                }
            });
            self.update_cpu_data(cpu_shart);
            setInterval(self.update_cpu_data,1000,cpu_shart);
        
        },

        update_ram_data:function(ram_shart){
            var self = this;
            ajax.jsonRpc('/server/monitoring/ram/informations', 'call', 
            {
            }).then(function(result){
                if ( ram_shart.data.labels.length < 17){
                    ram_shart.data.labels.push(result.current_seconds)
                }else{
                    ram_shart.data.labels.shift();
                    ram_shart.data.labels.push(result.current_seconds)
                }
                ram_shart.data.datasets.forEach((dataset) => {
                    if (dataset.data.length < 17){
                        dataset.data.push(result.percent_used);
                    }
                    else{
                        dataset.data.shift();
                        dataset.data.push(result.percent_used);
                    }
                $('#ram_info').text(result.used+'/'+result.total+' GB '+'('+result.percent_used+')');
                });

            ram_shart.update();
            })
               
           
        },

        do_ram_chart: function(){
            var self = this;
            var ctx = self.$el.find('#ram_usage');
            var ram_chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: ['rgba(68, 2, 207, 0.1)'],
                        borderColor: ['rgba(68, 2, 207, 1)'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    layout: {padding: {left: 0, right: 20, top: 5, bottom: 20}},
                    legend: {display: false,},
                    tooltips: {
                        enabled: false
                    },
                    scales: {
                        yAxes: [{ticks: {display: false ,beginAtZero: true,steps: 1,stepValue: 1,max: 100}}],
                        xAxes: [{ticks: {display: true}}]
                    },
                    elements: {
                        point:{
                            radius: 0
                        }
                    },
                }
            });
            self.update_ram_data(ram_chart);
            setInterval(self.update_ram_data,1000,ram_chart);
        },

        update_network_data : function(charts_name,networks_name){
            $.each(networks_name, function( index, value ) {
            ajax.jsonRpc('/server/net/informations', 'call', 
            {
                "data":{'natwork_name':value,},  
            }).then(function(result){
               
                var old_val = $('#'+value+'_info').attr('data').split('--');
                var new_val = [result.net_in,result.net_out];
                var delta_in = (new_val[0]-parseFloat(old_val[0])).toFixed(1).toString();
                var delta_out = (new_val[1]-parseFloat(old_val[1])).toFixed(1).toString();

                $('#'+value+'_info').text('In: '+delta_in+'Mbits/s Out: '+delta_out+'Mbits/s')
                $('#'+value+'_info').attr('data',result.net_in+'--'+result.net_out)


                if ( charts_name[index].data.labels.length < 17){
                    charts_name[index].data.labels.push(result.current_seconds)
                }else{
                    charts_name[index].data.labels.shift();
                    charts_name[index].data.labels.push(result.current_seconds)
                }
                charts_name[index].data.datasets.forEach((dataset) => {
                    if (dataset.data.length < 17){
                        dataset.data.push(((parseInt(delta_in) + parseInt(delta_out)) * 100) / result.speed);
                    }
                    else{
                        dataset.data.shift();
                        dataset.data.push(((parseInt(delta_in) + parseInt(delta_out)) * 100) / result.speed);
                    }
                });

                charts_name[index].update();
            })
          
        })

        },

        do_networks_charts : function(available_networks){
            var self = this;
            var charts_name = [];
            var networks_name = []
            $.each(available_networks, function( index, value ) {
                var html_elem_head = "<a class='nav-link' id='v-pills-"+value+"-tab' data-toggle='pill' href='#v-pills-"+value+"' role='tab' aria-controls='v-pills-home' aria-selected='true'>"+
                                        "<div><strong>Network adapter</strong></div>"+
                                        "<span>"+value+"</span><br/>"+
                                        "<span id='"+value+"_info' data='0--0'></span>"+
                                        "</a>";
                $('#v-pills-tab').append(html_elem_head);
                
                var html_elem_content = "<div class='tab-pane' id='v-pills-"+value+"' role='tabpanel' aria-labelledby='v-pills-"+value+"-tab'>"+
                                            "<div class='row'>"+
                                                "<div class='col-11'>"+
                                                    "<canvas id='network_"+value+"' max-width='300' max-height='300'></canvas>"+
                                                "</div>"+
                                            "</div>"+
                                        "</div>";

                $('#v-pills-tabContent').append(html_elem_content);

                var ctx = self.$el.find('#network_'+value);
                networks_name.push(value)
                charts_name.push(new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            data: [],
                            backgroundColor: ['rgba(255, 125, 71, 0.1)'],
                            borderColor: ['rgba(255, 125, 71, 1)'],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        layout: {padding: {left: 0, right: 20, top: 5, bottom: 20}},
                        legend: {display: false,},
                        tooltips: {
                            enabled: false
                        },
                        scales: {
                            yAxes: [{ticks: {display: false ,beginAtZero: true,steps: 1,stepValue: 1,max: 100}}],
                            xAxes: [{ticks: {display: true}}]
                        },
                        elements: {
                            point:{
                                radius: 0
                            }
                        },
                    }
                }));
              });

            self.update_network_data(charts_name,networks_name);
            setInterval(self.update_network_data,1000,charts_name,networks_name);
            },

        render: function() {
            var self = this;
            var super_render = this._super;
            var available_networks = [];
            var index_template = QWeb.render('im_server_monitoring.index',);
            $(index_template).prependTo(self.$el.find('.o_content'));
            self.do_cpu_chart();   
            self.do_ram_chart(); 
            ajax.jsonRpc('/server/net/available_networks', 'call', 
            {
            }).then(function(result){
                available_networks = result;
                self.do_networks_charts(available_networks); 
            }) 
        },

        reload: function () {
           
            window.location.href = this.href;
        },
    });
    core.action_registry.add('server_monitoring', ServerMonitoring);
    return ServerMonitoring;
    });
    