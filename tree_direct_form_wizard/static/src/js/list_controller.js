odoo.define('tree_direct_form_wizard.WizardListListRenderer', function (require) {
    "use strict";


   
    var ListRenderer = require("web.ListRenderer");


    var WizardListRenderer = ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'mouseover tr.o_data_row': 'do_show_form_now',
        }),
   
        do_show_form_now(e){
            var self = this;
            var xml_data =   $(e.currentTarget).attr('data-id')
            setTimeout(function(){ 
                var element = $("tr.o_data_row[data-id='"+xml_data+"']");
                if($("tr.o_data_row[data-id='"+xml_data+"']").length > 0 && $("tr.o_data_row[data-id='"+xml_data+"']").is(":hover")){     
                    var database_id = false;
                    var model = false;    
                    $.each(self.state.data, function( index, value ) {
                        if (value.id.split('_')[1]==xml_data.split('_')[1]){
                            database_id = value.res_id;
                            model = value.model;
                        }
                    });
                    if(model && database_id){
                        self.do_action({
                            type: 'ir.actions.act_window',
                            res_model:model ,
                            target: 'new',
                            views: [[false, 'form']],
                            res_id :database_id,
                        });
                    }

                }
                        }, 1500);
        
        },

      
    })
})
