odoo.define('ticketing_sale_pos.add_trains_table',function(require) {
    "use strict";
  
    var ajax = require('web.ajax');
    var xml_data = require('ticketing_sale_pos.xml_data'); 
    var compute_functions = require('ticketing_sale_pos.compute_functions'); 

    
    function add_stations_table(data){
        if(data !== undefined){
            var i;
            var y;
            var stations = []
            for (i = 0; i < data.length; i++) {
                for (y = 0; y < data[i].length; y++) {
                    if (jQuery.inArray(data[i][y].toString(), stations) === -1){
                        stations.push(data[i][y].toString());
                        var  train_table_stations = $($.parseHTML(xml_data.train_table_stations())).clone() ;
                        $(train_table_stations).find("td:eq(0)").text(data[i][y].toString()); 
                        $("#my-tab-stations tbody").append(train_table_stations);     
                    }  
                }
            }
           
            
        }
        

    } 

    
    
    function color_tr_time_table(clicked_tr){
        if(clicked_tr){
            $(clicked_tr).addClass('highlight').siblings().removeClass('highlight');
        }else{
            $("#my-tab-timetable tbody tr:visible:first").addClass('highlight').siblings().removeClass('highlight');
        }
       
    };
    
    function filtre_trains_by_time(calendar_data,clicked_tr=false) { 
        var table_trains_tr = $("#table-trains  tbody tr");
        var table_times_tr = $("#my-tab-timetable tbody tr");
        var selected_train_name = ""
        var arrival_time =  "";
        var current_time = $("#timeselect").val();
        var current_date = $("#date").val();
        // hide train if departure time < current time in all table(train and time)
            table_times_tr.each(function(){
                var checked_dye = calendar_data[$(this).find("td.train_name").text()].includes(current_date);
                if ( current_time >= $(this).find("td.departure_time").text() || !(checked_dye) ){ 
                    $(this).hide()
                }
                if(current_time < $(this).find("td.departure_time").text() && checked_dye){
                    $(this).show() 
                }
            
            });

            table_trains_tr.each(function(){
                var checked_dye = calendar_data[$(this).find("td.train_name").text()].includes(current_date);
                if ( current_time >= $(this).find("td.departure_time").text() || !(checked_dye) ){ 
                    $(this).hide()
                }
                if(current_time < $(this).find("td.departure_time").text() && checked_dye){
                    $(this).show() 
                }
          
            });
            
        // var i ;
        // for (i = 1; i < 5; i++) {
        //     var found =false;
        //     $("#table-trains tbody tr.path_"+i.toString()).each(function(){
        //         $(this).hide().removeClass('active');
                
        //         if($(this).find("td.departure_time").text() > arrival_time && found===false && arrival_time.length>2){
        //             $(this).show().addClass('active');
        //             arrival_time = $(this).find("td.arrival_time").text();
        //             found = true;
        //         }
                
        //     })
        // }    

        // color_tr_time_table(clicked_tr)

        // table_times_tr.each(function(){
        //     // dinamique selected train
        //     if($(this).hasClass("highlight") && $(this).is(':visible')){
        //         selected_train_name = $(this).find("td.train_name").text();
        //         arrival_time =  $(this).find("td.arrival_time").text()
        //     }
        // });
     
        // to hide all tr train table exepte a tr selected train 
        // table_trains_tr.each(function(){
        //     if($(this).find("td.train_name").text() !==selected_train_name && $(this).hasClass("path_0")){
        //         $(this).hide().removeClass('active');
        //     }else if ($(this).find("td.train_name").text()===selected_train_name && $(this).hasClass("path_0")) {
        //         $(this).show().addClass('active');
        //     }
        // })

        // to show tr train correspondence if exist
        // var i;  
        // console.log('arrival_time=>',arrival_time);
        // for (i = 1; i < 5; i++) {
        //     var found =false;
        //     $("#table-trains tbody tr.path_"+i.toString()).each(function(){
        //         $(this).hide().removeClass('active');
                
        //         if($(this).find("td.departure_time").text() > arrival_time && found===false && arrival_time.length>2){
        //             $(this).show().addClass('active');
        //             arrival_time = $(this).find("td.arrival_time").text();
        //             found = true;
        //         }
                
        //     })

        // }
        
        

     };
    function add_train_to_tr_time_table(value,path_type,data2){
        $("#my-tab-timetable tbody").attr({'path_type' : path_type,'data2' :  JSON.stringify(data2)})

        $.each(value, function(i,v){
            if (Object.keys(v).length>0){
                var  time_table_line = $($.parseHTML(xml_data.time_table_line())).clone() ;
                time_table_line.attr("data", JSON.stringify(v))    
                $(time_table_line).find("td:eq(0)").text(v["train_name"].toString()); 
                $(time_table_line).find("td:eq(1)").text(v["departure_time"].toString());  
                $(time_table_line).find("td:eq(2)").text(v["arrival_time"].toString());  
                $(time_table_line).find("td:eq(3)").text(v["duration"].toString());   
                // $(time_table_line).find("td:eq(4)").text(correspondence);   
                $(time_table_line).find("td:eq(5)").text(v["terminus"].toString());   
                $(time_table_line).find("td:eq(6)").text($('#input_train_class').children("option:selected").text());   
                $(time_table_line).find("td:eq(7)").text(v["distance"].toString());   
                $("#my-tab-timetable tbody:last-child").append(time_table_line);
            }        
        })   
       
    }

    function add_train_to_tr_trains_table(value){
        var stations = []
     
        $.each(value,function(i,v){
            if (Object.keys(v).length>0){
                stations.push(v["stations"])
                var  train_table_line = $($.parseHTML(xml_data.train_table_line())).clone() ;// .hide()
                train_table_line.addClass( "path_"+i);
                train_table_line.attr("data", JSON.stringify(v)) 
                $(train_table_line).find("td:eq(0)").text(v["train_name"].toString()); 
                $(train_table_line).find("td:eq(1)").text(v["departure_time"].toString()); 
                $(train_table_line).find("td:eq(2)").text(v["arrival_time"].toString()); 
                $(train_table_line).find("td:eq(3)").text(v["duration"].toString()); 
                // $(train_table_line).find("td:eq(4)").text(item["service"].toString()); 
                // $(train_table_line).find("td:eq(5)").text(item["type"].toString()); 
                // $(train_table_line).find("td:eq(6)").text(correspondence); 
                $(train_table_line).find("td:eq(7)").text(v["terminus"].toString()); 
                $(train_table_line).find("td:eq(8)").text($('#input_train_class').children("option:selected").text()); 
                $(train_table_line).find("td:eq(9)").text(v["distance"].toString()); 
                // $(train_table_line).find("td:eq(11)").text(v["reservation"].toString()); 
                $("#table-trains tbody").append(train_table_line);

            }
        })
        
        add_stations_table(stations);
    }


    

    function add_trains_and_station_to_table(data,calendar_data){
        var correspondence = "";
        if (data[0]==='simple'){
            add_train_to_tr_time_table(data[1],data[0],{});     
        }else if (data[0]==='multi'){
            add_train_to_tr_time_table(data[1],data[0],data[2]); 
        }
       
        filtre_trains_by_time(calendar_data);

        // compute_functions.compute_distance(); 
     

    };


   


        var request={
            'add_trains_and_station_to_table':add_trains_and_station_to_table,
            'filtre_trains_by_time':filtre_trains_by_time,
            'add_train_to_tr_trains_table':add_train_to_tr_trains_table,
        };

        return request;

});