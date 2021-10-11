odoo.define('tree_direct_form_wizard.WizardListListRenderer', function (require) {
    "use strict";


   
    var ListRenderer = require("web.ListRenderer");

    var timer = 0;

 
    var WizardListRenderer = ListRenderer.include({
   

        events: _.extend({}, ListRenderer.prototype.events, {
            'mouseover tr.o_data_row': '_do_show_wizard_form',
            'mouseleave tr.o_data_row': 'reset_timer',
           
        }),
        

        reset_timer:function(){
            timer = 0
        },
        do_show_form_now(e){
          
            var self = this;
            var xml_data =   $(e.currentTarget).attr('data-id').split('_')  
            var database_id = false;
            var model = false;    
            $.each(this.state.data, function( index, value ) {
                if (value.id.split('_')[1]==xml_data[1]){
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
        
        },

        _do_show_wizard_form: function(e) {
            setTimeout(() => {  timer = 1;this.do_show_form_now(e); }, 1000);
        },
    })
})