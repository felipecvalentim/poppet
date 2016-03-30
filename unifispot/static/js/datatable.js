/**
Core script to handle datatables, it will also handle updation of elements ( edit/delete)
**/
var DataTableWithEdit = function(table_id,datatable_config,api_url,modal) {

    var _this = this;
    var data_table = $("#"+table_id).DataTable(datatable_config);
    //handling addition of new element
    $('#'+modal+'-add-new').click(function(e) {
            $('#'+modal+'-save-button').val(api_url);
            $("#role-form-group").show();
            resetformfields(modal+"-form");
            $('#'+modal).modal();   
    });
    var toastr_options = {
        "closeButton": true,
        "debug": false,
        "positionClass": "toast-top-right",
        "onclick": null,
        "showDuration": "1000",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };
    var repopulateform = function(formid,url) {
        this.formid = formid;
        this.url    = url;

        $.ajax({
            type: 'get',
            url: url,
            data: {},
            success: function(data) {
                if (data.status) {
                    $.each(data.data, function(name, val){
                        var $el = $('[name="'+name+'"]'),
                            type = $el.attr('type');

                        switch(type){
                            case 'checkbox':
                                if (val !=0) {
                                    $el.prop('checked', true);
                                }
                                break;
                            case 'radio':
                                if(val){
                                    $el.filter('[value="'+val+'"]').attr('checked', 'checked');
                                }
                                break;
                            default:
                                $el.val(val);
                        }
                    });
                
                }
                else{
                        toastr.options= toastr_options;
                        var $toast = toastr['error']("ERROR", data.msg);               
                }
            }
        });
    }

    var resetformfields = function(formid) {
        $('#'+formid).find('input:text, input:password, input:file, select, textarea').val('');
        $('#'+formid).find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected')
    
    }
    // handle saving
    $('#'+modal+'-save-button').click(function(e) {
        //setup timeout for Post and enable error display
        e.preventDefault();        
        url = $(this).val();
        $.ajaxSetup({
            type: 'POST',
            timeout: 30000,
            error: function(xhr) {
                    $.unblockUI("#"+modal+"-form");
                    toastr.options= toastr_options;
                    var $toast = toastr['error']("ERROR", "Network timeout!!,Please try again later");
                 }
         });
        //block UI while form is processed
        $.blockUI({target: "#"+modal+"-form"});
        //$('#'+modal).modal('hide');
        $.post(url, $( "#"+modal+"-form" ).serialize(),function(data) {

                $.unblockUI("#"+modal+"-form");
                if(data.status){
                    toastr.options= toastr_options;
                    var $toast = toastr['success']("Success", data.msg);
                    $('#'+modal).modal('hide');
                    resetformfields();    
                    data_table.ajax.reload();
                    location.reload();
                }
                else{
                    toastr.options= toastr_options;
                    var $toast = toastr['error']("ERROR", data.msg);
                    $('#'+modal).modal();
                }
            },
            'json'// I expect a JSON response
        );
        return false;
    });

    //handle editing 
    $('#'+table_id).on( 'click', 'a.edit', function (e) {
        repopulateform("#"+modal+"-form",api_url+ this.id);
        $("#role-form-group").hide();
        $('#'+modal+'-save-button').val(api_url + this.id)
        $('#'+modal).modal();       
    });
    //handle deleting 
    $('#'+table_id).on( 'click', 'a.delete', function (e) {
        el = this;
        bootbox.confirm("You are about to delete an element,this action can't be undone. Are you Sure? ", function(r) {
            if (r) {
                //sent request to delete order with given id
                //block UI while request is processed
                $.blockUI({boxed: true});
                $.ajax({
                    type: 'delete',
                    url: api_url + el.id,
                    data: {},
                    success: function(b) {
                         $.unblockUI();
                        if (b.status) {
                            toastr.options= toastr_options;
                            var $toast = toastr['success']("Success", b.msg);
                            data_table.ajax.reload();                        
                        }
                        else{
                            toastr.options= toastr_options;
                            var $toast = toastr['error']("ERROR", b.msg);
                        }                                               
                    },
                    timeout: 30000,
                    error: function(xhr) {
                        $.unblockUI();
                        toastr.options= toastr_options;
                        var $toast = toastr['error']("ERROR", "Network timeout!!,Please try again later");
                    }
                    
                });
            
            }
        });
    
    });
    //handle refresh
    $('#'+modal+'-refresh-button').click(function(e) {

        data_table.ajax.reload();
    });
 
 

};
