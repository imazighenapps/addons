# -*- coding: utf-8 -*-
import json
import odoorpc
import werkzeug.utils
import time
from datetime import timedelta
from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
import networkx as nx
import xml.etree.ElementTree as ET
from networkx.algorithms.shortest_paths.weighted import single_source_dijkstra
import base64
import io
import datetime
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
try:
    import qrcode

except ImportError:
    _logger.debug('ImportError')
import ast
import requests
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

class TicketingController(http.Controller): 

    def condition(self,dic):
        return dic['key'] > 7


    def get_train_value(self,train,path):
        for line in train.station_line_ids:
            if str(line.station_id.name) == str(path[1][0]):
                departure_time = line.departure_time
        return departure_time


####################################################################################################################################
    def get_train_info(self,train_tab,G):
        GD = nx.DiGraph()
        train_value = []
        for train in train_tab :
            y=0
            start_station_line = end_station_line = False
            #to get edge of sub-graph,start and end station line 
            while  y < len(train[0].station_line_ids.station_id.ids)-1:
                if int(train[1][0]) == train[0].station_line_ids.station_id.ids[y] :
                    start_station_line = train[0].station_line_ids[y]

                if int(train[1][-1]) == train[0].station_line_ids.station_id.ids[y]  :
                    end_station_line = train[0].station_line_ids[y]

                GD.add_edge(str(train[0].station_line_ids.station_id.ids[y]),str(train[0].station_line_ids.station_id.ids[y+1]))
                y += 1 
            # to get train information
            if GD.has_node(train[1][0]) and GD.has_node(train[1][0]):
                if nx.has_path(GD, source=train[1][0], target=train[1][-1]) : 
                    # train = request.env['res.train'].search([('name','in',train[1])])
                    statio  = request.env['res.station'].search([('id','in',train[1])])
                    train_value.append({'train_name': train[0].name,
                                        # 'stations'  : [s.name for s in request.env['res.station'].search([('id','in',train[1])])],   
                                        'stations'  : [s.station_id.name for s in train[0].station_line_ids if s.station_id.id in [int(numeric_string) for numeric_string in train[1]] ],   
                                        
                                        'departure_time': self.format_hour(start_station_line.departure_time) ,
                                        'arrival_time' :self.format_hour(end_station_line.arrival_time),  
                                        'duration':self.format_hour(end_station_line.arrival_time - start_station_line.departure_time),  
                                        'terminus':train[0].station_line_ids[-1].station_id.name,
                                        'distance':"%.2f" % (single_source_dijkstra(G,source=train[1][0],target =train[1][-1],weight='weight')[0]),  
                                        'sub_reservation':train[0].sub_reservation,        
                                                 }) 
            GD.clear()    
        return train_value


   
    @http.route('/ticketing/get_disponible_train', type='json', auth='user')
    def get_disponible_train(self,**k):
        if k['stations'][0]!=k['stations'][1]:
            start = time.time()
            rail_network = request.env['rail.network'].search([('name','=','SNTF')])
            graph  = ast.literal_eval(rail_network.graph)
            G = nx.Graph()
            G.add_edges_from(graph)
            simple_train_tab = []
            simple_train_value=[]
            start_train_tab = []
            start_train_value = []
            end_train_tab = []
            end_train_value = []
        
            try:
                path = single_source_dijkstra(G,source=k['stations'][0],target =k['stations'][1],weight='weight')
            except:
                path = ()
            trains = request.env['res.train'].search([]) 
            i = 0
            train_tab = []
            if len(path)>0:
            #   for x in range(50):
                for train in trains :
                    trn=[]
                    if len(train.station_line_ids.station_id.ids)>0:
                        train_tab.append(train)
                        trn = [i for i in path[1] if int(i) in train.station_line_ids.station_id.ids]
                        if len(trn) >0 and  k['stations'][0] == trn[0]  and  k['stations'][1] == trn[-1]:
                            simple_train_tab.append((train,trn))


            if len(simple_train_tab) == 0:
                for traint in train_tab:
                    trn=[]
                    if len(traint.station_line_ids.station_id.ids)>0:
                        trn = [i for i in path[1] if int(i) in traint.station_line_ids.station_id.ids]
                        if len(trn) >0 and  k['stations'][0] == trn[0]:
                            start_train_tab.append((traint,trn))
                        if len(trn) >0 and  k['stations'][1] == trn[-1]:
                            end_train_tab.append((traint,trn))        


            simple_train_value = sorted(self.get_train_info(simple_train_tab,G), key=lambda k: k['departure_time']) 
            start_train_value  = sorted(self.get_train_info(start_train_tab,G), key=lambda k: k['departure_time']) 
            # first_arrival_time_tab = [train.get('arrival_time') for train in start_train_value]

            end_train_value    = sorted(self.get_train_info(end_train_tab,G), key=lambda k: k['departure_time']) 
            
            # a = filter(lambda d: d['type'] in keyValList, exampleSet)
            end = time.time()
            delta = end - start
            
            if len(simple_train_tab) == 0:
                return ['multi',start_train_value,end_train_value]  
            else :
                return ['simple',simple_train_value]         
        else :
            return []                

#############################################################################################################################################


    @http.route('/ticketing/get_starter_datas', type='json', auth='user')
    def get_starter_datas(self, **k):
        start_time = datetime.datetime.now()
        rail_network = request.env['rail.network'].search([('name','=','SNTF')])
        values={}
        values['stations'] = self.get_all_stations()
        values['departur_stations'] = self.get_departur_stations()

        values['travelers_profile'] = self.get_travelers_prfile()
        values['all_paths_trains_distance'] = {}#eval(rail_network[0].graph)
        values['default_travelers_profile'] = self.get_default_travelers_profile()
        values['default_travelers_profile_with'] = self.get_default_travelers_profile_with()
        values['classes'] = self.get_classes()
        values['calendar_data'] = eval(rail_network[0].calendar_data)
        values['printers_name'] = self.get_printers_name()
       
        end_time = datetime.datetime.now()
        duration = (end_time - start_time)

        # _logger.warning('\n ok ok rail_network[0].calendar_data  => %s',rail_network[0].calendar_data) 

        return values




    def get_classes(self):
        classes = request.env['res.class'].search_read([], ['name'],order="is_default desc")
        return classes

    def get_printers_name(self):
        printers = request.env['sntf.pos.printer'].search_read([], ['name','type'])
        return printers

    def get_travelers_prfile(self):
        # travelers_profile = request.env['traveler.profile'].search_read([('is_defaul','=',False)], ['name','category','personal_data_ids']) 
        travelers_profile = []
        travelers_profile_obj = request.env['traveler.profile'].search([('is_defaul','=',False)]) 
        for trp in travelers_profile_obj:
           travelers_profile.append({'id'                   : trp.id,
                                     'name'                 : trp.name,
                                     'personal_data_ids'    : [personal_data.name for personal_data in trp.personal_data_ids]
           }) 
        return travelers_profile

    def get_default_travelers_profile(self,):
        defaul_profile = request.env['traveler.profile'].search_read([('is_defaul','=',True)], ['name','discount','category'],limit=1) 
        return defaul_profile

    def get_default_travelers_profile_with(self,):
        defaul_profile_with = []
        defaul_profile = request.env['traveler.profile'].search([('is_defaul','=',True)],limit=1) 

        for dp in defaul_profile.category_with_ids:
            defaul_profile_with.append({'id':dp.category_Profil_id.id,'name':dp.category_Profil_id.name})
        return defaul_profile_with



    def get_departur_stations(self):
        emplyee = request.env['hr.employee'] .search([('user_id','=',request.env.user.id)])
        stations=[]
        if emplyee.station_id.id :
            if emplyee.lock_departure_station:
                stations = request.env['res.station'].search_read([('id','=',emplyee.station_id.id)], ['name'],order="name asc")
            else :
                strat_station = request.env['res.station'].search_read([('id','=',emplyee.station_id.id)], ['name'],order="name asc")
                stations = strat_station + request.env['res.station'].search_read([('id','!=',emplyee.station_id.id)], ['name'],order="name asc")

        else: 
            stations = request.env['res.station'].search_read([], ['name'],order="name asc") 

        return stations

    def get_all_stations(self):
        stations = request.env['res.station'].search_read([], ['name'],order="name asc")
        return stations
    
    def get_current_user_station(self):
        return 1

   

    def compute_distance(self,spath,train_name):  
        train = request.env['res.train'].search([('name',"=",train_name)]) 
        start_dist = 0
        end_dist   = 0
        for line in train.station_line_ids:
            if line.station_id.name == spath[0]:
                start_dist = line.departure_distance
            if  line.station_id.name == spath[-1] :
                end_dist = line.arrival_distance
        return  "%.2f" % (end_dist - start_dist)  

    

    @http.route('/ticketing/get_all_trains', type='json', auth='user')
    def get_all_trains(self,**k): 
        simple_path_found   = []
        start_station_paths = []
        end_station_paths   = []
        multiple_paths      = [] 
        for path_train_distance in k["all_paths_trains_distance"]:
            if k["station_ids"][0] == path_train_distance[0][0] and k["station_ids"][1] == path_train_distance[0][-1] and len(path_train_distance[1])>0 :
                simple_path_found = path_train_distance 
            if k["station_ids"][0] == path_train_distance[0][0]:
                start_station_paths.append(path_train_distance)    
            if k["station_ids"][1] == path_train_distance[0][-1]:
                end_station_paths.append(path_train_distance)    

        for ssp in start_station_paths:
            for esp in end_station_paths:
                intersection = list(set(ssp[0]) & set(esp[0]))
                if len(intersection)==1 and ssp[0][-1]  == esp[0][0] and ssp[1] != esp[1] and len(ssp[1])>0 and len(esp[1])>0:
                    multiple_paths.append([ssp,esp]) 
        if len(multiple_paths)>0:
            multiple_paths = multiple_paths[0]    
    
        if len(simple_path_found)>0:
            for sp in [simple_path_found]:
                for c_name in sp[3] :
                    if k['train_class'] not in c_name :
                        index = sp[3].index(c_name)
                        del sp[1][index]
                        del sp[2][index]

                  
        if len(multiple_paths)>0:
            i=0
            for mp in multiple_paths:
                if i==0:
                    for c_name in mp[3] :
                        if k['train_class'] not in c_name :
                            index = mp[3].index(c_name)
                            del mp[1][index]
                            del mp[2][index]
                i+=1
       
        return [simple_path_found,multiple_paths]

    def format_hour(self,fhour):
        hours = divmod(fhour * 60,60)[0]
        minutes = divmod(fhour * 60, 60)[1]    
        return "{:02d}".format(int(round(hours,5)))+":"+"{:02d}".format(int(round(minutes,5))) 


    def get_correspondence(self,tab,seg):
        data = []
        intersect =""
        for tb in tab:
            data.append(tb[0])
        if len(data)>0:
            intersect =str(",".join(set(seg).intersection(*data))) 
        return intersect


    @http.route('/ticketing/get_train_data', type='json', auth='user')
    def get_train_data(self,**k):
        trains = request.env['res.train'].search([('name',"in",k["trains_name"])],order="departure_time asc") 
        departure_time = ""
        arrival_time = ""
        trains_data=[]
        next_day = False
        for train in trains:  
            for line in train.station_line_ids:
                if line.station_id.name == k['stations'][0]:
                    departure_time  =   line.departure_time
                if line.station_id.name == k['stations'][1]:
                    if line.next_day:
                        next_day = True
                    arrival_time  =  line.arrival_time
            if next_day:
                first = arrival_time - 0
                last = 24 - departure_time
                delta = first + last
            else :    
                delta = arrival_time - departure_time   
            data = {'train_name':train.name,
                    'departure_time' :self.format_hour(departure_time),
                    'arrival_time':self.format_hour(arrival_time),
                    'duration':self.format_hour(delta),
                    'service':train.service_id.name,
                    'type':train.train_type_id.name,
                    'correspondence':self.get_correspondence(k["all_data"],k['stations']),
                    'terminus':train.station_line_ids[-1].station_id.name,
                    'distance': self.compute_distance([k['stations'][0],k['stations'][1]],train.name),
                    
                    }
            trains_data.append(data)
        return trains_data


    @http.route('/ticketing/get_tariff_category_with', type='json', auth='user')
    def get_tariff_category_with(self,**k):
        name_category_with =[]
        tariff_category = request.env['traveler.profile'].search([('id',"=",k["tariff_category_id"])])
        for tc in tariff_category.category_with_ids:
            name_category_with.append({"id":tc.category_Profil_id.id,"name":tc.category_Profil_id.name})
        return name_category_with

    @http.route('/ticketing/get_tariff_category_discount', type='json', auth='user')
    def get_tariff_category_discount(self,**k):
        tariff_category = request.env['traveler.profile'].search([('id',"=",k["tariff_category_id"])])
        return tariff_category.discount

     
    def compute_discount_price(self,price,traveler_profile_id):
        discount = request.env['traveler.profile'].search([('id','=',traveler_profile_id)]).discount
        return price - ((price * discount)/100)

    @http.route('/ticketing/get_amount', type='json', auth='user')
    def get_amount(self,**k): 
        start = time.time()
        data = k['data']
        price_path = 0
        ammount_total       = 0
        ammount_total_with  = 0
        trains = request.env['res.train'].search([('name',"in",data["train_name"])])
        i =0
        for train in trains:
            for price_line in train.scale_pricing_id.scale_calculation_ids:
                if price_line.start_distance <= int(float(data["distance"][i])) <= price_line.end_distance:
                    price_path += price_line.full_price 
            i+=1    
            if price_path == 0 :
               price_path = train.scale_pricing_id.minimum_perception 

        ammount_total = self.compute_discount_price(price_path,int(data["tariff_category"])) * int(data["number"])
        ammount_total_with = self.compute_discount_price(price_path,int(data["tariff_category_with"])) * int(data["number_with"])
        #to genirate a qr code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
        qr.add_data("Nouredine")
        qr.make(fit=True)
        img = qr.make_image()
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qrcode_img = base64.b64encode(buffer.getvalue())
        # self.update({'qr_code': qrcode_img,})
        end = time.time()
        delta = end - start
           
        _logger.warning('\n ok ok Runtime of the program is =>%s',delta)

        return [format(ammount_total + ammount_total_with, '.2f'),qrcode_img]
    
    
    def check_place_status(self,seat_number,train_id,date_time,start_date,duration,stations):
        reservation_from = datetime.datetime.strptime(date_time +' '+ start_date , '%Y-%m-%d %H:%M')
        reservation_to =  reservation_from + timedelta(hours=int(duration.split(':')[0])) + timedelta(minutes=int(duration.split(':')[1]))
        seat_state = False
        seat_id = request.env['place.taken'].search([('place_number','=',seat_number),
                                                     ('train_id','=',train_id),
                                                     ('state','!=',"cancel"),
                                                     ],limit=1)
                                                     
        if seat_id :
            if reservation_from >= seat_id.from_date and  reservation_to <= seat_id.to_date:
                seat_state = seat_id.state
        return [seat_state,seat_id]


    @http.route('/establish_connection', type='json', auth='none')
    def establish_connection(self,**k):
        password = self.decrypt(k.get('password'))
        login    = k.get('login')
        uid = request.session.authenticate('ticketing_test_data1', login , password)
        diagrams = self.get_remote_train_diagram(k.get('k'))
        return diagrams


    @http.route('/ticketing/get_train_diagram', type='json', auth='user')
    def get_train_diagram(self,**k):
        reservation_server = str(request.env['ir.config_parameter'].get_param('reservation_server'))
        database_name      = str(request.env['ir.config_parameter'].get_param('database_name'))
        server_port        = str(request.env['ir.config_parameter'].get_param('server_port'))
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache"}
        json_data = {"params":{"login":request.env.user.login,"password":self.encrypt(source=b"admin"),'k':k}}
        diagrams = requests.post("http://"+reservation_server+":"+server_port+"/establish_connection", data=json.dumps(json_data), headers=headers)
        return diagrams.json().get('result')


    def get_remote_train_diagram(self,k):
        diagrams = []
        all_seat_number = 0
        reserved_seat = 0
        css_class=['free','waiting_seat1','waiting_seat2','reserved_seat1']
        train_id = request.env['res.train'].search([('name','=',k['train_name'])])
      
        for line in train_id.train_car_line_ids:
            xml_data = base64.b64decode(line.car_typology_id.diagram).decode("utf-8").replace('xmlns:xlink="http://www.w3.org/1999/xlink"',' ').replace('xmlns="http://www.w3.org/2000/svg"',' ')
            myroot = ET.fromstring(xml_data)
            for elem in myroot:
                for e in elem.iter():
                    if e.tag=="text":
                        reservation_status,seat = self.check_place_status(e.text,train_id.id,k['date_time'],k['start_date'],k["duration"],k['stations'])
                        all_seat_number+=1
                        if reservation_status:
                            reserved_seat+=1
                            for path in elem.iter() :
                                if path.tag=="path" and path.attrib['class']=="free":
                                    # if reservation_status == 'temp_waiting':
                                    #     path.set('class','waiting_seat1') 
                                    #     if seat.user_id.id != request.session.uid:
                                    #         path.set('style','cursor: no-drop;')    
                                    #         e.set('style','cursor: no-drop;')   

                                    if reservation_status == "waiting":
                                        if seat.user_id.id == request.session.uid:
                                            _logger.warning('\n ok ok same user')
                                            path.set('class','waiting_seat1') 
                                            path.set('style','cursor: no-drop;')    
                                            e.set('style','cursor: no-drop;')   

                                        if seat.user_id.id != request.session.uid:
                                            _logger.warning('\n ok ok not same user')
                                            path.set('class','waiting_seat2') 
                                            path.set('style','cursor: no-drop;')    
                                            e.set('style','cursor: no-drop;')   

                                    if reservation_status == "reserved":
                                        path.set('class','reserved_seat1') 
                                        path.set('style','cursor: no-drop;')    
                                        e.set('style','cursor: no-drop;')   

                                          

            diagrams.append(ET.tostring(myroot).decode())     
        return {"diagrams":diagrams,
                "reserved_seat":reserved_seat,
                "all_seat_number":all_seat_number}


    @http.route('/ticketing/seat_reserving_or_free', type='json', auth='user')
    def seat_reserving_or_free(self,**k):
        seat_obj=()
        to_create = True
        reservation_from = datetime.datetime.strptime(k['data']['date_time']+' '+k['data']['reservation_date_time_from'], '%Y-%m-%d %H:%M') - timedelta(hours=1)
        reservation_to =  reservation_from + timedelta(hours=int(k['data']['duration'].split(':')[0])) + timedelta(minutes=int(k['data']['duration'].split(':')[1]))
        
        # reservation_to =  datetime.datetime.strptime(k['data']['date_time']+' '+k['data']['reservation_date_time_to'], '%Y-%m-%d %H:%M')
        train_id = request.env['res.train'].search([('name','=',k['data']['train_name'])])
        for line in train_id.seat_line_ids:
            if int(line.number)==int(k['seat_name']):
                seat_obj = line
                for reservation in line.reservation_seat_line_ids:
                    if reservation_from == reservation.reservation_date_time_from and reservation_to ==reservation.reservation_date_time_to:
                        reservation.unlink()
                        to_create = False
                if to_create :
                    seat_obj.reservation_seat_line_ids.create({'reservation_date_time_from': reservation_from,
                                                                'reservation_date_time_to': reservation_to, 
                                                                'seat_line_id': seat_obj.id, 
                                                                'state':"waiting",
      
      
                                                                                })

    def get_train_obj(self,train_name): 
        train_id = request.env['res.train'].search([('name','=',train_name)])
        if len(train_id) > 0 :
            return train_id
        else:
            return False    


    def get_station_id(self,station_names):
        station_ids =[]
        for st_name in station_names:
            station_ids.append(request.env['res.station'].search([('name','=',st_name)]).id)
        return station_ids
        
    def get_single_station_id(self,station_name):
        return request.env['res.station'].search([('name','=',station_name)]).id
       


    def get_class_id(self,class_name):
        return  request.env['res.class'].search([('name','=',class_name)]).id
 


    @http.route('/ticketing/create_order', type='json', auth='user')
    def create_order(self,**k):
        order_obj = request.env["ticketing.order"]
        data_order = k['data_order']
        _logger.warning('\n ok ok data_order=>%s',data_order)
        if data_order['tariff_category_with'] == 'Sélectionner...' : data_order['tariff_category_with'] = False
        station_line_ids  = []
        station_line_data = []
        train_hours_data  = []
        train_hours_ids   = []
        order_type="sale" 
        # to add train hour information
        for dt in data_order['trains']:
            train_obj = self.get_train_obj(dt['train_number'])
            if train_obj.sub_reservation:
                order_type = "booking"
            train_hours_data.append({'train_id':train_obj.id,
                                     'departure_time' : dt['departure_time']  ,
                                     'arrival_time' : dt['arrival_time']  ,
                                     'duration' : dt['duration']  ,
                                     'correspondence_id' : self.get_single_station_id(dt['correspondence'])  ,
                                     'terminus' : self.get_single_station_id(dt['terminus'])  ,
                                     'class_id' : self.get_class_id(dt['train_class']) , 
                                    })
        for v in train_hours_data:
            train_hours_ids.append((0,0,v))    



        #to get stop stations
        for station_id in self.get_station_id(data_order['stop_stations']) :
            station_line_ids.append((0,0,{'station_id':station_id,}))

        # place_taken_ids = self.create_place_taken(data_order,train_hours_data)

        data = {
                'name':self.get_order_name(),
                'company_id': request.env.user.company_id.id, 
                'departure_hour'                  : data_order['date_time'].split(' ')[1],
                'date'                            : data_order['date_time'].split(' ')[0], 
                'class_id'                        : data_order['class'], 
                'journal_id'                      : 6, 
                'sale_type'                       : data_order['sale_type'],
                'course'                          : data_order['course'],
                'traveler_profile_id'             : data_order['tariff_category'],
                'passengers_number'               : data_order['number'],
                'passengers_discount'             : data_order['discount'],     
                'traveler_profile_with_id'        : data_order['tariff_category_with'],
                'companion_number'                : data_order['number_with'],
                'companion_discount'              : data_order['discount_with'],    
                
                'start_station_id'                : data_order['start_station'],
                'end_station_id'                  : data_order['end_station'],
                # 'train_id'                        : self.get_train_obj(data_order['train_name'][0]).id,
                'start_correspondence_station_id' : False,
                'end_correspondence_station_id'   : False,
                'arrival_time_to_correspondence'  : 0,

            #   'train_line_ids'                  : train_line_ids ,       
                'amount_total'                    : data_order['amount_total'],
                'distance'                        : data_order['distance'],
                'station_line_ids'                : station_line_ids,
                'train_hours_ids'                 : train_hours_ids,  
                'type'                            : order_type,  
                'place_taken_ids'                 : place_taken_ids,   
                'qr'                              : self.get_qr_code(data_order['date_time'].split(' ')[0],data_order['date_time'].split(' ')[1],data_order['start_station'],data_order['end_station']), 
                          }

     
        new_id = request.env['ticketing.order'].create(data)
        
        return new_id.id

    def get_qr_code(self,date,departure_hour,start_station,end_station):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
        qr.add_data({"date":date,
                     "time":departure_hour,
                     "start_station":start_station,   
                     "end_station":end_station,   
                        })
        qr.make(fit=True)
        img = qr.make_image()
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue())



    def get_order_name(self,):
        user = request.env.user
        employee  =  request.env['hr.employee'].search([('user_id','=',user.id)])
        name = employee.station_id.code +'-'+employee.counter
        sequence = request.env['ir.sequence'].next_by_code("ticketing.order")
        name+='-'+ str(sequence)+'-SNTF'
        return name



    def create_place_taken(self,data_order,train_hours_data):
        i = 0
        date_taken = data_order['date_time'].split(' ')[0] 
        place_taken_ids = []
        for train in train_hours_data:
            station_tab = self.get_stattion_tab(train['train_id'],data_order['start_station'],data_order['end_station'],train['correspondence_id'],data_order['stop_stations'],i)
            i+=1
            data = {'train_id'    :  train['train_id'],
                    'date'        :  date_taken,
                    'number_of_place_taken':int(data_order['number_with']) + int(data_order['number']),
                    'stations'    : str(station_tab),
                    'car_number'   : self.get_car_id(train['train_id'],date_taken,station_tab), 

                    }

            
            new_id = request.env['place.taken'].create(data)
            place_taken_ids.append(new_id.id)
        return place_taken_ids        

    def get_car_id(self,train_id,date_taken,station_tab):
        car_1 = 1
        car_2 = 1
        car_3 = 1
        car = 1
        tab=[]
      
        place_taken = request.env['place.taken'].search([('train_id','=',train_id),('date','=',date_taken)])

        for p in place_taken:
            for s in station_tab:
                if s in eval(p.stations):
                    if p.car_number == 1:
                        car_1+=p.number_of_place_taken
                    if p.car_number == 2:
                        car_2+=p.number_of_place_taken
                    if p.car_number == 3:
                        car_3+=p.number_of_place_taken

        tab = [car_1,car_2,car_3]    
        tab.sort()
        if tab[0]==car_2:
            car = 2
        if tab[0]==car_3:
            car = 3     
        return car

    def get_stattion_tab(self,train_id,start_station,end_station,correspondence_id,stop_station,index):
        train_obg = request.env['res.train'].search([('id','=',train_id)])
        correspondence_obj = request.env['res.station'].search([('id','=',correspondence_id)])
        station_tab=[]
        if not(correspondence_id) :
            station_tab = stop_station
        else :
            if index==0:
                station_tab = stop_station[0: stop_station.index(correspondence_obj.name)]
            if index==1:
                station_tab = stop_station[stop_station.index(correspondence_obj.name):-1]
        if len(station_tab)>1:
            station_tab.pop()
     
        return station_tab


    def get_station_name(self,station_id):
        return request.env['res.station'].search([('id','=',station_id)],).name

    @http.route('/ticketing/get_pdf_report', type='json', auth='user')
    def get_pdf_report(self,**k):
       
        report_name = "ticketing_sale.ticketing_order_report_dec"
        pdf = request.env.ref(report_name).sudo().render_qweb_pdf([int(k['id'])],data={'report_type': 'pdf'})[0]

        return base64.b64encode(pdf)

    @http.route('/ticketing/change_state_place_taken', type='json', auth='user')
    def change_state_place_taken(self,**k):
        reservation_server = str(request.env['ir.config_parameter'].get_param('reservation_server'))
        database_name      = str(request.env['ir.config_parameter'].get_param('database_name'))
        server_port        = str(request.env['ir.config_parameter'].get_param('server_port'))
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache"}
        json_data = {"params":{"login":request.env.user.login,"password":self.encrypt(source=b"admin"),'k':k}}
        result = requests.post("http://"+reservation_server+":"+server_port+"/ticketing/change_state_place_taken/remote", data=json.dumps(json_data), headers=headers)
        _logger.warning('\n ok ok result.json()=>%s',result.json())
        return result.json().get('result')
        

    # Change state place taken
    @http.route('/ticketing/change_state_place_taken/remote', type='json', auth='none')
    def change_state_place_taken_remote(self,**k):
        password = self.decrypt(k.get('password'))
        login    = k.get('login')
        action = ""
        
        uid = request.session.authenticate('ticketing_test_data1', login , password)
        k = k.get('k')
        train = request.env['res.train'].search([('name','=',k.get('data').get('train_name'))])
        from_date = datetime.datetime.strptime(k['data']['date']+" " +k['data']['reservation_date_time_from'], '%Y-%m-%d %H:%M')
        to_date   = from_date + datetime.timedelta(hours=int(k['data']['duration'].split(':')[0]),seconds=int(k['data']['duration'].split(':')[1])*60) 
        seat_id = request.env['place.taken'].search([('place_number','=',k['data']['seat_name']),
                                                       ('train_id','=',train.id,),
                                                       ('state','!=',"cancel"),
                                                       ('from_date','=',from_date),
                                                       ('to_date','=',to_date),
                                                     ],limit=1)

        if seat_id:                                              
            if seat_id.state == "waiting":
                seat_id.unlink()
                action ='unlink'

        else :
            action='create'
            seat_id = request.env['place.taken'].create({'place_number': k['data']['seat_name'],
                                              'train_id'    :  train.id, 
                                              'from_date'   :   from_date,            
                                              'to_date'     :   to_date,        
                                              'stations'    :    k['data']['stop_stations'],         
                                              #  'car_number'  :   k['data']['seat_name'],        
                                              'state'       :   "waiting",
                                              'user_id'     :   request.session.uid, 
                                                    })
        _logger.warning('\n ok ok ********************** action=>%s',action)                                            
        return action                                            

                                               


    @http.route('/ticketing/place_monitoring', type='json', auth='user')
    def place_monitoring(self,**k):
        _logger.warning('\n ok ok in locale place_monitoring')
     
        reservation_server = str(request.env['ir.config_parameter'].get_param('reservation_server'))
        database_name      = str(request.env['ir.config_parameter'].get_param('database_name'))
        server_port        = str(request.env['ir.config_parameter'].get_param('server_port'))
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache"}
        json_data = {"params":{"login":request.env.user.login,"password":self.encrypt(source=b"admin"),'k':k}}
        result = requests.post("http://"+reservation_server+":"+server_port+"/ticketing/place_monitoring/remote", data=json.dumps(json_data), headers=headers)
        return result.json().get('result')


    @http.route('/ticketing/place_monitoring/remote', type='json', auth='none')
    def place_monitoring_remote(self,**k):
      
        password = self.decrypt(k.get('password'))
        login    = k.get('login')
        uid = request.session.authenticate('ticketing_test_data1', login , password)
        # _logger.warning('\n ok ok in remote place_monitoring')
        start = time.time()
        train_data = k.get('k').get('train_data')
        result={}
        reservation_from = datetime.datetime.strptime(train_data.get('reservation_date') +' '+ train_data.get('departure_time') , '%Y-%m-%d %H:%M')
        reservation_to =  reservation_from + timedelta(hours=int(train_data.get('duration').split(':')[0])) + timedelta(minutes=int(train_data.get('duration').split(':')[1]))
        place_taken_obj = request.env['place.taken'].search([
                        ('train_id','=',request.env['res.train'].search([('name','=',train_data.get('train_name'))]).id),
                        # ('state','!=','cancel'),
                        ('to_date','>=',reservation_from),
                        ('from_date','<=',reservation_to),


            ])

        for pl_tk in place_taken_obj:
            if reservation_from <= pl_tk.to_date and pl_tk.from_date <= reservation_to:
                result[pl_tk.place_number] = [pl_tk.state,pl_tk.user_id.id]

        # _logger.warning('\n ok ok result=>%s',result)    
        end = time.time()
        delta = end - start
        # _logger.warning('\n ok ok delta=>%s',delta)  
        
        return   result    



    def encrypt(self,source, encode=True):

        key = b"Far1d3$e"  
        key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
        IV = Random.new().read(AES.block_size)  # generate IV
        encryptor = AES.new(key, AES.MODE_CBC, IV)
        padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
        source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
        data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
        return base64.b64encode(data).decode("latin-1") if encode else data

    def decrypt(self, source, decode=True):
        key = b"Far1d3$e"  
        if decode:
            source = base64.b64decode(source.encode("latin-1"))
        key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
        IV = source[:AES.block_size]  # extract the IV from the beginning
        decryptor = AES.new(key, AES.MODE_CBC, IV)
        data = decryptor.decrypt(source[AES.block_size:])  # decrypt
        padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
        if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
            raise ValueError("Invalid padding...")
        return data[:-padding]  # remove the padding

    
    @http.route('/check_the_availability_of_the_reservation_server', type='json', auth='none')
    def check_the_availability_of_the_reservation_server(self,**k):
        return 1


