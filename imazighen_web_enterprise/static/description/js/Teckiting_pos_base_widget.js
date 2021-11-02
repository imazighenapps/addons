odoo.define('ticketing_sale_pos.view_ticketing_sale_pos', function (require) {

    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var QWeb = core.qweb;
    var all_paths_trains_distance = []
    var calendar_data = {}
    var printers_name = []

    var QWeb = core.qweb;
    var trains_table = require('ticketing_sale_pos.add_trains_table'); 
    var compute_functions = require('ticketing_sale_pos.compute_functions'); 
    var xml_data = require('ticketing_sale_pos.xml_data'); 
    var order_manager = require('ticketing_sale_pos.order_manager'); 
    var session = require('web.session');
    var view_ticketing_sale_pos = AbstractAction.extend({
       
        events: {
            "change .stations": 'change_stations',
            "change #TariffCategory": 'change_tariff_category',
            "change #TariffCategoryWith": 'change_tariff_category_with',
            "click #my-tab-timetable" : "change_time_table", 
            "change #input_train_class" : "change_stations", 
            "change .tariff_category_profile_sale ": 'compute_amount_filtre_category_profile',
            "change #amount_given": 'compute_rest', 
            "click #booking_btn": 'show_booking_view',
            "click .seat": 'seat_clicked' , 
            "click #print_order": 'create_order', 
            "change #timeselect": 'filtre_train_by_date_time',
            "change #date": 'filtre_train_by_date_time', 
            "change .to_compute": 'compute_amount', 
            "click .close_modal": 'close_modal',
     

        },
        
        close_modal:function(){
            $("#reservation_block").slideToggle("fast");
        },
        
        compute_amount: function(event){
            compute_functions.compute_amount();
        },

        create_order : function(event){
            order_manager.create_order();

        },
     

        filtre_train_by_date_time : function(event){
            
            trains_table.filtre_trains_by_time(calendar_data);
            this.select_train(); 
        },

   
        compute_rest :function(event){
            var amount_given = parseFloat($(event.currentTarget).val());
            var amount_total = parseFloat($('#amount_total').val());
            var rest = amount_given - amount_total;
            $('#rest').val(rest);

        },

        seat_clicked : function(event){
            var nb_place = 0; 
            var table_station_line = $("#my-tab-stations tbody tr");
            var table_trains = $("#table-trains  tbody tr");
            // init data
            var data = {"train_name":[],"date":$("#date").val(),"seat_name" : $(event.currentTarget).find('text').text(),
                "reservation_date_time_from":"","reservation_date_time_to":"","duration":"","stop_stations":[],
            }
            if(table_station_line.length>0){
                table_station_line.each(function(index){
                    data['stop_stations'].push($(this).find("td.station_name").text());
                })
            }
            if(table_trains.length>0){
                table_trains.each(function(index){
                    data['train_name']  = $(this).find("td.train_name").text();
                    data['reservation_date_time_from'] = $(this).find("td.departure_time").text();
                    data['reservation_date_time_to'] = $(this).find("td.arrival_time").text();
                    data['duration'] = $(this).find("td.duration").text();
                 })
               
            }
            var all_path = $(event.currentTarget).find('path');
            ajax.jsonRpc('/ticketing/change_state_place_taken', 'call', 
                                                {
                                                 "data":data,  
                                                }).then(function(result){
                                                    var all_seat = $('.seat');
                                                    console.log("result=>",result);
                                                    if (result=='create'){
                                                        all_path.each(function(){
                                                            $(this).addClass('waiting_seat1').removeClass('free');     
                                                        })
                                                        all_seat.each(function(){
                                                            if ($(this).find('path').attr('class') =='waiting_seat1'){
                                                                nb_place +=1;
                                                            }
                                                        })
                                                    } 
                                                    if(result=='unlink'){
                                                        all_path.each(function(){
                                                            $(this).addClass('free').removeClass('waiting_seat1');
                                                        })
                                                        all_seat.each(function(){
                                                            if ($(this).find('path').attr('class') =='waiting_seat1'){
                                                                nb_place +=1;
                                                            }
                                                        })
                                                    }   
                                                    console.log('nb_place=>',nb_place) ;
                                                    $('#number').val(nb_place);

                                                })

            
        },

      

        show_booking_view : function(event){

            $("#reservation_block").slideToggle("fast");
            var table_times = $("#my-tab-timetable tbody tr");
            var train_name  = false;
            var date_time   = $("#date").val().replace("/", "-").replace("/", "-")
            var start_date  = "";
            var duration    = "";
            var stations    = [];
            var table_station_line = $("#my-tab-stations tbody tr"); 
            if(table_station_line.length>0){
                table_station_line.each(function(index){
                    stations.push($(this).find("td.station_name").text());
                })
            }

            table_times.each(function(index){
               if($(this).hasClass('highlight')){
                    train_name=$(this).find('td.train_name').text();
                    start_date = $(this).find('td.departure_time').text();
                    duration  = $(this).find('td.duration').text();
               }   
            })
            $(".carousel-inner").empty();
            $(".carousel-indicators").empty();
           
            if(table_times){
                ajax.jsonRpc('/ticketing/get_train_diagram', 'call', 
                {   "start_date":start_date,
                    "duration":duration,
                    "train_name":train_name,
                    "date_time":date_time,
                    "stations":stations,

                }).then(function(data){
                    var i;
                    var index 
                    var diagrams = data["diagrams"];
                    $('#seats_status').replaceWith("Sièges vides : "+(data["all_seat_number"] - data["reserved_seat"])+"/"+data["all_seat_number"]) 
                    for (i = 0; i < diagrams.length; i++) {
                        var  carousel_item = $($.parseHTML(xml_data.carousel_item())).clone() ;
                        index = i+1
                        if (i === 0){
                            carousel_item.addClass('active');
                            carousel_item.append(diagrams[i]);
                            $(".carousel-inner").append(carousel_item);
                            $(".carousel-indicators").append("<li data-target='#carouselIndicators' data-slide-to='"+ i +"' class='active'>"+index+"</li>");
 
                        }else{
                            carousel_item.append(diagrams[i]);
                            $(".carousel-inner").append(carousel_item);
                            $(".carousel-indicators").append("<li data-target='#carouselIndicators' data-slide-to='"+ i +"'>"+index+"</li>");
                                }
                            }
                        }
                        );
    
            }    
       
        },
        // to compute amount  and filtre category profile
        compute_amount_filtre_category_profile : function(event){  
            // compute_functions.compute_amount();
            compute_functions.compute_amount();
            // filtre category profile
            var category_choosed  = $('#category').find('input:checked').attr('id');
            var tariff_category     = $('#TariffCategory').find('option');
            tariff_category.each(function(index){
                if($(this).attr("category")===category_choosed && $(this).attr("category")!=="undefined"){
                
                    $(this).removeAttr("disabled");
                }
                else{
                    $(this).attr('disabled', 'disabled');
                }
              });   

             $('#TariffCategory').find('#0').attr('selected','selected');
          



        },

        get_date_clock_default:function(){
            var dt = new Date();
            var time =("0" + dt.getHours()).slice(-2)+ ":" + ("0" + dt.getMinutes()).slice(-2);
            var twoDigitMonth   =  ("0" + (dt.getMonth()+1)).slice(-2);
            var twoDigitDay     =  ("0" + (dt.getDate())).slice(-2);
            var date = dt.getFullYear()+ "-" + twoDigitMonth +"-"+ twoDigitDay;
            $("#date").val(date);  
            $('#timeselect').val(time);
        },

        get_date_clock_loop:function(){
            var dt = new Date();
            var time =("0" + dt.getHours()).slice(-2)+ ":" + ("0" + dt.getMinutes()).slice(-2);
            var twoDigitMonth   =  ("0" + (dt.getMonth()+1)).slice(-2);
            var twoDigitDay     =  ("0" + (dt.getDate())).slice(-2);
            var date = dt.getFullYear()+ "-" + twoDigitMonth +"-"+ twoDigitDay;
            $("#date").val(date);  
            $('#timeselect').val(time);
   
        },

        // to get trains list
        change_stations : function(event){
            $("#my-tab-timetable tbody tr").remove();
            $("#table-trains tbody tr").remove();
            $("#my-tab-stations tbody tr").remove();
            var self = this;
            var stations = new Array();
            var train_class = $('#input_train_class').children("option:selected").val();
            $("select.stations").each(function(){
                stations.push($(this).find('option:selected').attr("id"));
            });
       
            
            ajax.jsonRpc('/ticketing/get_disponible_train', 'call', 
            { "stations":stations,
               "train_class":train_class,

            }).then(function(data){

                trains_table.add_trains_and_station_to_table(data,calendar_data);
                self.select_train();  
             

            })


            },

        select_train : function(event){
            var first_train ;
            var data2 ;
            var path_type ;
            var second_train;
            second_train = {};
            if (event === undefined){
                $("#my-tab-timetable tbody tr:visible:first").addClass('highlight').siblings().removeClass('highlight');     
                first_train = $("#my-tab-timetable tbody tr:visible:first").attr('data');
                first_train !== undefined && first_train.length >= 10 ? first_train = JSON.parse(first_train) : first_train={};
                data2 = $("#my-tab-timetable tbody").attr('data2');
                data2 !== undefined && data2.length >= 2 ? data2 = JSON.parse(data2) : data2={};
                path_type = $("#my-tab-timetable tbody").attr('path_type');
                $.each(data2,function(i,v){    
                    if( first_train["arrival_time"] < v["departure_time"]){
                        second_train = v     
                    } 
                
                })

            }else{
               $(event.target).parent().addClass('highlight').siblings().removeClass('highlight');
               first_train = $(event.target).parent().attr('data');
               first_train !== undefined && first_train.length >= 10 ? first_train = JSON.parse(first_train) : first_train={};
               data2 = $(event.target).parent().parent().attr('data2');
               data2 !== undefined && data2.length >= 2 ? data2 = JSON.parse(data2) : data2={};
               path_type = $(event.target).parent().parent().attr('path_type');
               $.each(data2,function(i,v){  
                    if( first_train["arrival_time"] < v["departure_time"]){
                        second_train = v     
                    } 
                
                })
            }

            $("#table-trains tbody").empty();
         
            if (path_type=="multi"){
                if (Object.keys(second_train).length>0){
                    trains_table.add_train_to_tr_trains_table([first_train,second_train])

                }else{
                    trains_table.add_train_to_tr_trains_table([first_train])
                    $('body').append($($.parseHTML(xml_data.alert_no_correspondence())).clone());
                    setTimeout(function() {$('#alert_no_correspondence_train').remove();}, 5000);

                }
            }else{
                trains_table.add_train_to_tr_trains_table([first_train])
            }
        compute_functions.compute_amount();    
        },       


        /* to get discount for tariff category with*/  
        change_tariff_category_with : function(event){
            var tariff_category_id = $(event.target).children(":selected").attr("id");
            $("#discount_traveler_profile_with").val("0");
            if ($("#TariffCategoryWith").find('option:selected').attr('id')==0){
                $("#NumberWith").val("0"); 
            }else{
                $("#NumberWith").val("1");  
            }
            
            if(tariff_category_id !== undefined){
                ajax.jsonRpc('/ticketing/get_tariff_category_discount', 'call', 
                {
                    "tariff_category_id":tariff_category_id,
                }).then(function(discount){
                    $("#discount_traveler_profile_with").val(discount);
                 
                            }
                        );  
            }
        },


        /* to ger tariff category with and discount */            
        change_tariff_category: function(event){
            var tariff_category_id = $(event.target).children(":selected").attr("id");
            ajax.jsonRpc('/ticketing/get_tariff_category_with', 'call', 
            {
                "tariff_category_id":tariff_category_id,
            }).then(function(data){
                $("#TariffCategoryWith").find('option').remove();
                $("#TariffCategoryWith").append("<option id='0'>Sélectionner...</option>");
                var i;
                for (i = 0; i < data.length; i++) {
                    $("#TariffCategoryWith").append("<option id="+data[i].id +">"+data[i].name+"</option>");
                
                }

                        }
                    );
            ajax.jsonRpc('/ticketing/get_tariff_category_discount', 'call', 
            {
                "tariff_category_id":tariff_category_id,
            }).then(function(discount){
                $("#discount_traveler_profile").val(discount);
                        }
                    );                 

        },     
        
        change_time_table : function(event){
            this.select_train(event)
          
        },
    
        shortcutkey : function(event){
            if (event.which === 119){
                if($("#print_order").prop('disabled')){ 
                    $("#reservation_block").slideToggle("fast");
                }
             
            }
        },


        init: function(parent, context) {           
            var data =[];
            this._super(parent, context);
            var self = this;
            var down = true;
            $(document).keydown(function( e ){
                if (down){
                    self.shortcutkey(e)
                    down = false;
                }
            })
            $(document).keyup(function( e ){
                    down = true;
            })

            if (context.tag == 'view_ticketing_sale_pos') {
        
                
            }
        },

        willStart: function() {
            return $.when(ajax.loadLibs(this), this._super());
        },
        


        start: function() {
            console.log(' in start');
            var self = this;
            self.render();
            self.get_date_clock_loop();
            setInterval(self.get_date_clock_loop,120000);
            setInterval(compute_functions.compute_distance,1000);
            setInterval(self.toggle_print_button,500);
            setInterval(self.refresh_seat,2000);
            
        
        },

    

        refresh_seat:function(event){
            // console.log('in refresh_seat');
         
            if($('#reservation_block').is(':visible')){
                var table_times = $("#my-tab-timetable tbody tr");
                var reservation_date   = $("#date").val().replace("/", "-").replace("/", "-")
                var train_data = {};
                table_times.each(function(index){
                    if($(this).hasClass('highlight')){
                        train_data = JSON.parse($(this).attr('data'))    
                    }   
                })
                train_data['reservation_date']=reservation_date;
                ajax.jsonRpc('/ticketing/place_monitoring', 'call', 
                    {  
                        "train_data":train_data,
                    }).then(function(data){
                        $.each(data, function(place, state_user) {
                            var diagram = $('#reservation_block').find("text");
                            diagram.each(function(index) {
                                if( $.trim(place)==$.trim($(this).text()) ){
                                    var all_path = $(this).parent().parent().find('path');
                                    if(state_user[0]==="waiting"){
                                        if (state_user[1] !== session.uid){
                                            $(all_path).addClass('waiting_seat2').removeClass("free");
                                            $(all_path).css('cursor','no-drop');
                                            $(this).css('cursor','no-drop');
                                        }
                                        if(state_user[1] === session.uid){
                                            $(all_path).addClass('waiting_seat1').removeClass("free");
                                            $(all_path).css('cursor','pointer');
                                            $(this).css('cursor','pointer');
                                        }
                                    }
                                    if(state_user[0]==="reserved"){
                                        $(all_path).addClass('reserved_seat1').removeClass("waiting_seat1");
                                        $(all_path).addClass('reserved_seat1').removeClass("free");
                                        $(all_path).css('cursor','no-drop');
                                        $(this).css('cursor','no-drop');
                                    }
                                    if(state_user[0]==="cancel"){
                                        $(all_path).addClass('free').removeClass("waiting_seat1");
                                        $(all_path).addClass('free').removeClass("reserved_seat1");
                                        $(all_path).css('cursor','pointer');
                                        $(this).css('cursor','pointer'); 
                                    }
                                
                                    
                                }
                                
                            
                            })
                       
                        }); 
                        
                    }
               )
            }
        },

        toggle_print_button:function(){
            var table_trains = $("#table-trains  tbody tr");
            if(table_trains.length>0){
                $('#print_order').removeAttr("disabled").removeClass('btn-secondary').addClass('btn-primary');    
                table_trains.each(function(){
                    if($.parseJSON($(this).attr("data")).sub_reservation){
                        $('#booking_btn').removeAttr("disabled").removeClass('btn-secondary').addClass('btn-primary'); 
                        $('#print_order').attr("disabled","disabled").removeClass('btn-primary').addClass('btn-secondary');
                        var all_seat = $('.seat');
                        var nb_place = 0;
                        all_seat.each(function(){
                            if ($(this).find('path').attr('class') =='waiting_seat1'){
                                nb_place +=1;
                                }
                            })
                        if(nb_place>0){
                            $('#print_order').removeAttr("disabled").removeClass('btn-secondary').addClass('btn-primary');  
                            $('#booking_btn').removeAttr("disabled").removeClass('btn-secondary').addClass('btn-primary'); 

                        }else{
                            $('#print_order').attr("disabled","disabled").removeClass('btn-primary').addClass('btn-secondary');
                        }
                    }else{
                        $('#booking_btn').attr("disabled","disabled").removeClass('btn-primary').addClass('btn-secondary'); 
                        $('#print_order').removeAttr("disabled").removeClass('btn-secondary').addClass('btn-primary');  
                    }
                })
                 
            }else{
                $('#booking_btn').attr("disabled","disabled").removeClass('btn-primary').addClass('btn-secondary'); 
                $('#print_order').attr("disabled","disabled").removeClass('btn-primary').addClass('btn-secondary');
            }


        },

        getPrintersStatus : function(print_name){
             qz.printers.find(print_name).then(function(printer) {
                 qz.printers.startListening(printer).then(function(){
                     qz.printers.getStatus().then(function() {
                         
                     });
                 });
             }).catch(function(e) {console.error(e); });
            
         },

        check_availability_printers : function(){
            var self = this;      
            $.each(printers_name, function(index, value){
                if (value['type']==="roller"){
                    qz.printers.setPrinterCallbacks(function(evt){
                        if (evt.statusCode===0){
                            $("#roller").removeClass("btn-danger").addClass("btn-success");
                        }else{
                            $("#roller").removeClass("btn-success").addClass("btn-danger");
                        }
                    });
                    qz.printers.startListening(value['name']).then(function(){})     
                    self.getPrintersStatus(value['name']);

                }
              });

           
         },
    
         
        render: function() {
            var self = this;
            self.acces_params();
            // self.launchQZ();
            self.startConnection({ retries: 50, delay: 2 });
            console.log(' in render');
            var super_render = this._super;
            ajax.jsonRpc('/ticketing/get_starter_datas', 'call', {}).then(function(datas){
                all_paths_trains_distance = datas['all_paths_trains_distance'];
                calendar_data             = datas['calendar_data'];
                printers_name             = datas['printers_name'];     
                var index_template = QWeb.render('ticketing_sale_pos.index', { datas});
                $(index_template).prependTo(self.$el.find('.o_content'));
                self.get_date_clock_default(); 
                self.check_availability_printers();
                // setInterval(self.check_availability_printers,1000);   
                });
        },
        
      
        reload: function () {
            console.log(' in reload');
            window.location.href = this.href;
        },
        
        launchQZ :function() {
            var self = this;
            if (!qz.websocket.isActive()) {
                window.location.assign("qz:launch");
                //Retry 5 times, pausing 1 second between each attempt
                self.startConnection({ retries: 5, delay: 1 });
            }
        },

        startConnection : function (config) {
            var self = this;
            if (!qz.websocket.isActive()) {
                qz.websocket.connect(config).then(function() {
                }).catch(self.handleConnectionError);
            } else {
                // displayMessage('An active connection with QZ already exists.', 'alert-warning');
            }
        },

        /// Helpers ///
        handleConnectionError : function (err) {
        updateState('Error', 'danger');
        if (err.target != undefined) {
            if (err.target.readyState >= 2) { //if CLOSING or CLOSED
                displayError("Connection to QZ Tray was closed");
            } else {
                displayError("A connection error occurred, check log for details");
                console.error(err);
            }
        } else {
            displayError(err);
        }
        },

       
        acces_params : function(){
            /// Authentication setup ///
qz.security.setCertificatePromise(function(resolve, reject) {
resolve("-----BEGIN CERTIFICATE-----\n" +
"MIIFAzCCAuugAwIBAgICEAIwDQYJKoZIhvcNAQEFBQAwgZgxCzAJBgNVBAYTAlVT\n" +
"MQswCQYDVQQIDAJOWTEbMBkGA1UECgwSUVogSW5kdXN0cmllcywgTExDMRswGQYD\n" +
"VQQLDBJRWiBJbmR1c3RyaWVzLCBMTEMxGTAXBgNVBAMMEHF6aW5kdXN0cmllcy5j\n" +
"b20xJzAlBgkqhkiG9w0BCQEWGHN1cHBvcnRAcXppbmR1c3RyaWVzLmNvbTAeFw0x\n" +
"NTAzMTkwMjM4NDVaFw0yNTAzMTkwMjM4NDVaMHMxCzAJBgNVBAYTAkFBMRMwEQYD\n" +
"VQQIDApTb21lIFN0YXRlMQ0wCwYDVQQKDAREZW1vMQ0wCwYDVQQLDAREZW1vMRIw\n" +
"EAYDVQQDDAlsb2NhbGhvc3QxHTAbBgkqhkiG9w0BCQEWDnJvb3RAbG9jYWxob3N0\n" +
"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtFzbBDRTDHHmlSVQLqjY\n" +
"aoGax7ql3XgRGdhZlNEJPZDs5482ty34J4sI2ZK2yC8YkZ/x+WCSveUgDQIVJ8oK\n" +
"D4jtAPxqHnfSr9RAbvB1GQoiYLxhfxEp/+zfB9dBKDTRZR2nJm/mMsavY2DnSzLp\n" +
"t7PJOjt3BdtISRtGMRsWmRHRfy882msBxsYug22odnT1OdaJQ54bWJT5iJnceBV2\n" +
"1oOqWSg5hU1MupZRxxHbzI61EpTLlxXJQ7YNSwwiDzjaxGrufxc4eZnzGQ1A8h1u\n" +
"jTaG84S1MWvG7BfcPLW+sya+PkrQWMOCIgXrQnAsUgqQrgxQ8Ocq3G4X9UvBy5VR\n" +
"CwIDAQABo3sweTAJBgNVHRMEAjAAMCwGCWCGSAGG+EIBDQQfFh1PcGVuU1NMIEdl\n" +
"bmVyYXRlZCBDZXJ0aWZpY2F0ZTAdBgNVHQ4EFgQUpG420UhvfwAFMr+8vf3pJunQ\n" +
"gH4wHwYDVR0jBBgwFoAUkKZQt4TUuepf8gWEE3hF6Kl1VFwwDQYJKoZIhvcNAQEF\n" +
"BQADggIBAFXr6G1g7yYVHg6uGfh1nK2jhpKBAOA+OtZQLNHYlBgoAuRRNWdE9/v4\n" +
"J/3Jeid2DAyihm2j92qsQJXkyxBgdTLG+ncILlRElXvG7IrOh3tq/TttdzLcMjaR\n" +
"8w/AkVDLNL0z35shNXih2F9JlbNRGqbVhC7qZl+V1BITfx6mGc4ayke7C9Hm57X0\n" +
"ak/NerAC/QXNs/bF17b+zsUt2ja5NVS8dDSC4JAkM1dD64Y26leYbPybB+FgOxFu\n" +
"wou9gFxzwbdGLCGboi0lNLjEysHJBi90KjPUETbzMmoilHNJXw7egIo8yS5eq8RH\n" +
"i2lS0GsQjYFMvplNVMATDXUPm9MKpCbZ7IlJ5eekhWqvErddcHbzCuUBkDZ7wX/j\n" +
"unk/3DyXdTsSGuZk3/fLEsc4/YTujpAjVXiA1LCooQJ7SmNOpUa66TPz9O7Ufkng\n" +
"+CoTSACmnlHdP7U9WLr5TYnmL9eoHwtb0hwENe1oFC5zClJoSX/7DRexSJfB7YBf\n" +
"vn6JA2xy4C6PqximyCPisErNp85GUcZfo33Np1aywFv9H+a83rSUcV6kpE/jAZio\n" +
"5qLpgIOisArj1HTM6goDWzKhLiR/AeG3IJvgbpr9Gr7uZmfFyQzUjvkJ9cybZRd+\n" +
"G8azmpBBotmKsbtbAU/I/LVk8saeXznshOVVpDRYtVnjZeAneso7\n" +
"-----END CERTIFICATE-----\n" +
"--START INTERMEDIATE CERT--\n" +
"-----BEGIN CERTIFICATE-----\n" +
"MIIFEjCCA/qgAwIBAgICEAAwDQYJKoZIhvcNAQELBQAwgawxCzAJBgNVBAYTAlVT\n" +
"MQswCQYDVQQIDAJOWTESMBAGA1UEBwwJQ2FuYXN0b3RhMRswGQYDVQQKDBJRWiBJ\n" +
"bmR1c3RyaWVzLCBMTEMxGzAZBgNVBAsMElFaIEluZHVzdHJpZXMsIExMQzEZMBcG\n" +
"A1UEAwwQcXppbmR1c3RyaWVzLmNvbTEnMCUGCSqGSIb3DQEJARYYc3VwcG9ydEBx\n" +
"emluZHVzdHJpZXMuY29tMB4XDTE1MDMwMjAwNTAxOFoXDTM1MDMwMjAwNTAxOFow\n" +
"gZgxCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJOWTEbMBkGA1UECgwSUVogSW5kdXN0\n" +
"cmllcywgTExDMRswGQYDVQQLDBJRWiBJbmR1c3RyaWVzLCBMTEMxGTAXBgNVBAMM\n" +
"EHF6aW5kdXN0cmllcy5jb20xJzAlBgkqhkiG9w0BCQEWGHN1cHBvcnRAcXppbmR1\n" +
"c3RyaWVzLmNvbTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBANTDgNLU\n" +
"iohl/rQoZ2bTMHVEk1mA020LYhgfWjO0+GsLlbg5SvWVFWkv4ZgffuVRXLHrwz1H\n" +
"YpMyo+Zh8ksJF9ssJWCwQGO5ciM6dmoryyB0VZHGY1blewdMuxieXP7Kr6XD3GRM\n" +
"GAhEwTxjUzI3ksuRunX4IcnRXKYkg5pjs4nLEhXtIZWDLiXPUsyUAEq1U1qdL1AH\n" +
"EtdK/L3zLATnhPB6ZiM+HzNG4aAPynSA38fpeeZ4R0tINMpFThwNgGUsxYKsP9kh\n" +
"0gxGl8YHL6ZzC7BC8FXIB/0Wteng0+XLAVto56Pyxt7BdxtNVuVNNXgkCi9tMqVX\n" +
"xOk3oIvODDt0UoQUZ/umUuoMuOLekYUpZVk4utCqXXlB4mVfS5/zWB6nVxFX8Io1\n" +
"9FOiDLTwZVtBmzmeikzb6o1QLp9F2TAvlf8+DIGDOo0DpPQUtOUyLPCh5hBaDGFE\n" +
"ZhE56qPCBiQIc4T2klWX/80C5NZnd/tJNxjyUyk7bjdDzhzT10CGRAsqxAnsjvMD\n" +
"2KcMf3oXN4PNgyfpbfq2ipxJ1u777Gpbzyf0xoKwH9FYigmqfRH2N2pEdiYawKrX\n" +
"6pyXzGM4cvQ5X1Yxf2x/+xdTLdVaLnZgwrdqwFYmDejGAldXlYDl3jbBHVM1v+uY\n" +
"5ItGTjk+3vLrxmvGy5XFVG+8fF/xaVfo5TW5AgMBAAGjUDBOMB0GA1UdDgQWBBSQ\n" +
"plC3hNS56l/yBYQTeEXoqXVUXDAfBgNVHSMEGDAWgBQDRcZNwPqOqQvagw9BpW0S\n" +
"BkOpXjAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQAJIO8SiNr9jpLQ\n" +
"eUsFUmbueoxyI5L+P5eV92ceVOJ2tAlBA13vzF1NWlpSlrMmQcVUE/K4D01qtr0k\n" +
"gDs6LUHvj2XXLpyEogitbBgipkQpwCTJVfC9bWYBwEotC7Y8mVjjEV7uXAT71GKT\n" +
"x8XlB9maf+BTZGgyoulA5pTYJ++7s/xX9gzSWCa+eXGcjguBtYYXaAjjAqFGRAvu\n" +
"pz1yrDWcA6H94HeErJKUXBakS0Jm/V33JDuVXY+aZ8EQi2kV82aZbNdXll/R6iGw\n" +
"2ur4rDErnHsiphBgZB71C5FD4cdfSONTsYxmPmyUb5T+KLUouxZ9B0Wh28ucc1Lp\n" +
"rbO7BnjW\n" +
"-----END CERTIFICATE-----\n");
});

qz.security.setSignatureAlgorithm("SHA512"); // Since 2.1
// qz.security.setSignaturePromise(function(toSign) {
//     return function(resolve, reject) {
//         resolve(); // remove this line in live environment
//     };
//         });


},       




    
    });
    
    
    
    
    core.action_registry.add('view_ticketing_sale_pos', view_ticketing_sale_pos);
    return view_ticketing_sale_pos;
    });
    