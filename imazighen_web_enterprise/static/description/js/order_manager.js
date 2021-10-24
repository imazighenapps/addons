odoo.define('ticketing_sale_pos.order_manager',function(require) {
    "use strict";
  
    var ajax = require('web.ajax');

    function get_data_order(){
        var order_data={
            'trains'                :   [],
            'start_station'         :   "",        
            'end_station'           :   "",
            'date_time'             :   "",
            'class'                 :   "", 
            'stop_stations'         :   [], 
            'distance'              :   0,
            'category'              :   "",
            'sale_type'             :   "",
            'course'                :   "",
            'tariff_category'       :   "",
            'number'                :   "",
            'discount'              :   "",
            'tariff_category_with'  :   "",
            'number_with'           :   "",
            'discount_with'         :   "",
            'amount_total'          :   "",
            'path_type'             :   "",
            'sale_type'             :   "", 
            "seat_numbers"          :   [],

                    };

        order_data['start_station'] = $("#StartStation").find('option:selected').attr("id");
        order_data['end_station']   = $("#EndStation").find('option:selected').attr("id");
        order_data['date_time']     =  $("#date").val()+' '+$("#timeselect").val();
        order_data['class'] = $("#input_train_class").find('option:selected').attr("id");
        order_data['category'] = $("#category").find('radio:checked').attr('id');
        order_data['sale_type'] = $("#SaleType").find('option:selected').attr('id');
        order_data['course'] = $("#SaleDetail").find('option:selected').attr('id');
        order_data['tariff_category'] = $("#TariffCategory").find('option:selected').attr('id');
        order_data['number'] = $("#number").val();
        order_data['discount'] = $("#discount_traveler_profile").val();
        order_data['tariff_category_with'] = $("#TariffCategoryWith").find('option:selected').text();
        order_data['number_with'] = $("#NumberWith").val();
        order_data['discount_with'] = $("#discount_traveler_profile_with").val();
        order_data['amount_total'] = $("#amount_total").val();
        var table_trains = $("#table-trains  tbody tr");
        console.log('table_trains=>',table_trains);
        if(table_trains.length>1){
            order_data['path_type'] = "correspondance";
        }
        table_trains.each(function(index){
            var seats_number = [];
            if (JSON.parse($(this).attr("data")).sub_reservation){
                var all_seat = $('.seat');
                all_seat.each(function(){
                    if ($(this).find('path').attr('class') =='waiting_seat1'){
                        console.log('this seats number=>',$(this).text());
                        seats_number.push()
                        }
                    })

                
            }
            order_data['distance'] += parseFloat($(this).find("td.distance").text());
            order_data['trains'].push({'train_number' : $(this).find("td.train_name").text(),
                                        'departure_time' : $(this).find("td.departure_time").text(), 
                                        'arrival_time'   : $(this).find("td.arrival_time").text(),
                                        'duration'       : $(this).find("td.duration").text(),
                                        'correspondence' : $(this).find("td.correspondence").text(),
                                        'terminus'       : $(this).find("td.terminus").text(),
                                        'train_class'    : $(this).find("td.train_class").text(),
                                        'distance'       : $(this).find("td.distance").text(),   
                                        'sub_reservation':    JSON.parse($(this).attr("data")).sub_reservation,                                  
                                        });
                                      
            
        })
           
       
      
        var table_station_line = $("#my-tab-stations tbody tr");
        if(table_station_line.length>0){
            table_station_line.each(function(index){
                order_data['stop_stations'].push($(this).find("td.station_name").text());
                
                
            })
           
        }


        return order_data
    }


    

    function create_order(){
        var data_order = get_data_order();
        console.log("data_order=>",data_order);
        ajax.jsonRpc('/ticketing/create_order', 'call', 
            {"data_order":data_order,
                }).then(function(id){
                    ajax.jsonRpc('/ticketing/get_pdf_report', 'call', 
                        {"id":id,
                            }).then(function(data){
                                var config = qz.configs.create("EPSON TM-T88V Receipt5"); 
                                var data = [{ 
                                    type: 'pdf',
                                    format: 'base64',
                                    data: data 
                                    }];
                                console.log("config=>",config);            
                                qz.print(config, data).then(function(){ 
                                    $("#EndStation").val("nothing").change();
                                 })

                                                    }); 

        });

   



    }
    
        var request={
           
            'create_order'     : create_order,
        };

        return request;

});