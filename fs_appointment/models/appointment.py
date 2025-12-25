from odoo import models, fields, api
from datetime import datetime, timedelta,time
import logging
_logger = logging.getLogger(__name__)


class Azzzppointment(models.Model):
    _name = 'appointment.availability'

class Appointment(models.Model):
    _name = 'appointment.appointment'
    _description = 'Appointment'

    name                = fields.Char(string='Name', required=True)
    appointment_date    = fields.Date(string='Appointment Date', required=True)
    start_time          = fields.Float(string='Start Time', required=True)
    end_time            = fields.Float(string='End Time', required=True)
    details             = fields.Text(string='Details')
    status              = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed'),('started', 'Started'),('completed', 'Completed'),('cancelled','Cancelled')], default='draft', string='Status')
    
    customer_id         = fields.Many2one('res.partner', string='Customer')
    service_id          = fields.Many2one('appointment.service', string='Services')
    employee_ids        = fields.Many2many('hr.employee', string='Employees')

    start_date_time     = fields.Datetime(string='Appointment start')
    end_date_time       = fields.Datetime(string='Appointment end')

    


    def action_confirm(self):
        self.status = 'confirmed'
 
    def action_start(self):
        self.status = 'started'

    def action_complete(self):
        self.status = 'completed'

    def action_cancel(self):
        self.status = 'cancelled'


    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            strat_date_time,end_date_time = self._compute_start_date_time()
            self.start_date_time = strat_date_time
            self.end_date_time = end_date_time
            self.appointment_date = strat_date_time.date() 
            self.start_time = strat_date_time.time().hour + strat_date_time.time().minute /60 
            self.end_time = end_date_time.time().hour + end_date_time.time().minute /60 

    def _compute_start_date_time(self):
        if self.service_id:
            last_appointment = self._get_last_appointment()
            if last_appointment:
                calendar = self.service_id.calendar_id
                end_time = last_appointment.end_time
                last_date  = last_appointment.appointment_date
                last_date_time = datetime.combine(last_date, datetime.min.time()) + timedelta(hours=end_time)
                start_date_time =  last_date_time
                end_date_time = start_date_time + timedelta(hours=self.service_id.duration)
                if end_date_time.time() > time(int(calendar.closing_hour),int((calendar.closing_hour - int(calendar.closing_hour)) * 60)):
                    start_date_time = datetime.combine( (start_date_time + timedelta(days=1)).date(),time(hour=int(calendar.opening_hour), minute=int((calendar.opening_hour - int(calendar.opening_hour)) * 60)) )
                    end_date_time = start_date_time + timedelta(hours=self.service_id.duration)

                while True:
                    weekday = start_date_time.weekday()
                    if weekday == 0 and not calendar.monday:
                        start_date_time += timedelta(days=1)
                        end_date_time = start_date_time + timedelta(hours=self.service_id.duration)
                    elif weekday == 1 and not calendar.tuesday:
                        start_date_time += timedelta(days=1)
                        end_date_time = start_date_time + timedelta(hours=self.service_id.duration)
                    elif weekday == 2 and not calendar.wednesday:
                        start_date_time += timedelta(days=1)
                        end_date_time = start_date_time + timedelta(hours=self.service_id.duration)
                    elif weekday == 3 and not calendar.thursday:
                        start_date_time += timedelta(days=1)
                        end_date_time = start_date_time + timedelta(hours=self.service_id.duration)
                    elif weekday == 4 and not calendar.friday:
                        start_date_time += timedelta(days=1)
                        end_date_time = start_date_time + timedelta(hours=self.service_id.duration)
                    elif weekday == 5 and not calendar.saturday:
                        start_date_time += timedelta(days=1)
                        end_date_time = start_date_time + timedelta(hours=self.service_id.duration)
                    elif weekday == 6 and not calendar.sunday:
                        start_date_time += timedelta(days=1)
                        end_date_time = start_date_time + timedelta(hours=self.service_id.duration)
                    else:
                        break

        return  (start_date_time,end_date_time)   
                        
               

    def _get_last_appointment(self):
        last_appointment = False
        # if self.id:
        _logger.warning('\n ok ok self.id=>%s',self.id.origin)
        appointments = self.search([('service_id', '=', self.service_id.id),('id','!=',self.id.origin)])
        if appointments:
            sorted_appointments = sorted(appointments, key=lambda app: (app.appointment_date, app.end_time), reverse=True)
            last_appointment = sorted_appointments[0]

        return last_appointment

