odoo.define('ticketing_sale_pos.compute_functions',function(require) {
    "use strict";
  
    var ajax = require('web.ajax');

    function get_selected_trains_information_for_reservation(){
        var table_times = $("#my-tab-timetable tbody tr");
        var data ={};
        data['date_time'] = $("#date").val().replace("/", "-").replace("/", "-")
        table_times.each(function(){
            if($(this).hasClass("highlight")){
                data['train_name']  = $(this).find("td.train_name").text();
                data['reservation_date_time_from'] = $(this).find("td.departure_time").text();
                data['reservation_date_time_to'] = $(this).find("td.arrival_time").text();
                data['duration'] = $(this).find("td.duration").text();
                
                
            }
        })
        return data
    }
   
    function compute_distance(data){
        var table_trains = $("#table-trains  tbody tr");
        var distance=0;
        var last_distance = parseFloat($("#global_distance").val());
        if(table_trains.length>0){
            table_trains.each(function(index){
                distance += parseFloat($(this).find("td.distance").text());
            })
        }   
        
        if(last_distance!= distance){
            $("#global_distance").val(distance);
            compute_amount();
        }
        
    }

    
        
    function compute_amount(){
      
        var table_trains = $("#table-trains  tbody tr");
        var data = {
            "train_name":[],
            "distance":[],
            "sale_type":"",
            "path_type":"",
            "tariff_category":"",
            "number":"",
            "tariff_category_with":"",
            "number_with":"",
        }
        $("#amount_total").val(parseFloat(0.00).toFixed(2));
        $("#qr_code").empty();
        // $('#print_order').attr("disabled","disabled").removeClass('btn-primary').addClass('btn-secondary');
        if(table_trains.length>0){
            table_trains.each(function(index){
                data['train_name'].push($(this).find("td.train_name").text());
                data['distance'].push($(this).find("td.distance").text());
            })
           
        }
        data['sale_type'] = $("#SaleType").find('option:selected').text();
        data['path_type'] = $("#SaleDetail").find('option:selected').text();
        data['tariff_category'] = $("#TariffCategory").find('option:selected').attr('id');
        data['number'] = $("#number").val();
        data['tariff_category_with'] = $("#TariffCategoryWith").find('option:selected').attr('id');
        data['number_with'] = $("#NumberWith").val();
        $('#total_passengers').val(parseInt($("#NumberWith").val())+parseInt($("#number").val()));

        // console.log("ok ok data=>",data);
        
        if(data['train_name'].length > 0) {
            ajax.jsonRpc('/ticketing/get_amount', 'call', 
            {"data":data,         
                }).then(function(datas){
                    $("#amount_total").val(datas[0]);
                    
                    var image = new Image();
                    image.src = 'data:image/png;base64,'+datas[1];
                    image.height = "142";
                    $("#qr_code").append(image);
                    
                    // $('#print_order').removeAttr("disabled").removeClass('btn-secondary').addClass('btn-primary');
                        return true
                    });
        } 
    }
 


        var request={
            'compute_distance':compute_distance,
            'compute_amount':compute_amount,
            'get_selected_trains_information_for_reservation':get_selected_trains_information_for_reservation,
        };

        return request;

});