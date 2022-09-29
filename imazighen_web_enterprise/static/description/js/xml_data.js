odoo.define('ticketing_sale_pos.xml_data',function(require) {
    "use strict";
  


    function time_table_line () { 
       return ""+
                "<tr>"+
                    "<td class='train_name text-center'  width='9%' height='23px'></td>"+
                    "<td class='departure_time text-center' width='16%' height='23px'></td>"+
                    "<td class='arrival_time text-center' width='16%' height='23px'></td>"+
                    "<td class='duration text-center' width='7%' height='23px'></td>"+
                    "<td class='correspondence text-center' width='18%' height='23px'></td>"+
                    "<td class='terminus text-center' width='16%' height='23px'></td>"+
                    "<td class='train_class text-center' width='11%' height='23px'></td>"+
                    "<td class='distance text-center' width=7%' height='23px'></td>"+
                "</tr>";
        
    };

    function train_table_line(){
        return ""+
                  "<tr >"+
                        "<td class='train_name text-center' width='6%' height='23px' ></td>"+
                        "<td class='departure_time text-center' width='10%' height='23px'></td>"+
                        "<td class='arrival_time text-center' width='10%' height='23px'></td>"+
                        "<td class='duration text-center' width='6%' height='23px'></td>"+
                        "<td class='service text-center' width='12%' height='23px'></td>"+
                        "<td class='type text-center' width='12%' height='23px'></td>"+
                        "<td class='correspondence text-center' width='15%' height='23px'></td>"+
                        "<td class='terminus text-center' width='15%' height='23px'></td>"+
                        "<td class='train_class text-center' width='7%' height='23px'></td>"+
                        "<td class='distance text-center' width='7%' height='23px'></td>"+
                  "</tr>"
    }
    function train_table_stations(){
        return ""+
                "<tr>"+
                    "<td class='col-12 station_name'></td>"+
                "</tr>"

    }

    function carousel_item(){
        return "<div class='carousel-item'> </div>"
           
    }  
    
    
    function alert_no_correspondence(){
        return ""+
        "<div id='alert_no_correspondence_train' class='alert alert-danger alert-dismissible fade show' role='alert' style='width:40%;position: fixed;top: 35%;left: 16%; background: red;color: white;'>"+
        "<strong>Attention !</strong> Aucun train de correspondance"+
        "<button type='button' style='color: white;' class='close' data-dismiss='alert' aria-label='Close'>X"+
          "<span aria-hidden='true'>&times;</span>"+
        "</button>"+  
      "</div>"
    }

    // function alert_no_correspondence(){
    //     return ""+
    //     "<div id='alert_no_correspondence_train' class='alert alert-danger alert-dismissible fade show' role='alert' style='width:40%;position: fixed;top: 35%;left: 16%; background: red;color: white;'>"+
    //     "<strong>Attention !</strong> Veuillez noter qu'il n'y a pas de train de correspondence"+
    //     "<button type='button' style='color: white;' class='close' data-dismiss='alert' aria-label='Close'>X"+
    //       "<span aria-hidden='true'>&times;</span>"+
    //     "</button>"+  
    //   "</div>"
    // }

    
    var request={
            'time_table_line':time_table_line,
            'train_table_line':train_table_line,
            'train_table_stations':train_table_stations,
            'carousel_item':carousel_item,
            'alert_no_correspondence':alert_no_correspondence,

        };


        return request;

});