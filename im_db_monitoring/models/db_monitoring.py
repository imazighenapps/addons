from odoo import models, fields, api
import logging
from odoo.http import request
from odoo.addons.im_db_monitoring.controllers.main import DatabaseMonitoring as DBM

_logger = logging.getLogger(__name__)

class DatabaseMonitoring(models.Model):
    _name = 'db.monitoring'



    
    def save_history(self):

        model_names=["db.general.status.history","db.query.statistics.history","db.tuples.history",
                     "db.tuples.fetched.returned.history","db.block.io.history","db.table.size.history"]

        fonction_names = ["get_general_status","get_query_statistics","get_tuples_in","get_tuples_out",
                        "get_block_io","get_table_sizes"]

        for i in range(len(model_names)-1):
            self.get_and_create_data(model_names[i],fonction_names[i])




    def get_and_create_data(self,model_name,fonction_name):
        record = self.env[model_name].sudo().search([("status","=","draft")])
        current_time = fields.Datetime.now()
        data = eval(f"DBM.{fonction_name}(self)")
        _logger.warning("\n ok ok data =>%s",data)  

        if not record.id :
            data["status"]="draft"
            data["date_from"] = current_time
            self.env[model_name].sudo().create(data)
        else:

          data["date_to"] = current_time
          data["status"] = "valid"
          if model_name not in ["db.general.status.history","db.table.size.history"]:
            for field in data:
                if  isinstance(data[field], int) or isinstance(data[field], float):
                    data[field] = data[field]  - eval(f"record.{field}")

          record.write(data)  