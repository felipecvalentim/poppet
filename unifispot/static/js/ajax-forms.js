/**
Core script to handle ajax forms. It can handle both posting data for creating/updation as well parsing data from get request.
**/
var AjaxForm = function(formid,url) {

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
                        var $el = $('#'+formid+' [name="'+name+'"]'),
                            type = $el.attr('type');
                        switch(type){
                            case 'checkbox':
                                if (val !=0) {
                                    $el.prop('checked', true);
                                }
                                break;
                            case 'radio':
                                $el.filter('[value="'+val+'"]').attr('checked', 'checked');
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

    //main function to initiate the module

    this.formid = formid;
    this.url    = url;
    $('#'+this.formid +'-save').attr('href',url);
           
    // handle saving
    $('#'+this.formid +'-save').click(function(e) {
        //setup timeout for Post and enable error display
        e.preventDefault();        
        url = $(this).attr('href');
        btnid = $(this).attr('id');
        formid = btnid.slice(0, -5); // button id will be created by adding -save to formid
        $.ajaxSetup({
            type: 'POST',
            timeout: 30000,
            error: function(xhr) {
                    $.unblockUI();
                    toastr.options= toastr_options;
                    var $toast = toastr['error']("ERROR", "Network timeout!!,Please try again later");
                 }
         });
        //block UI while form is processed
        $.blockUI({boxed: true});
        $.post(url, $( "#"+formid ).serialize(),function(data) {
                $.unblockUI();
                if(data.status){
                    toastr.options= toastr_options;
                    var $toast = toastr['success']("Success", data.msg);
                }
                else{
                    toastr.options= toastr_options;
                    var $toast = toastr['error']("ERROR", data.msg);
                }
            },
            'json'// I expect a JSON response
        );
        return false;
    });

    repopulateform(formid,url);

        

        
    
};

function create_site_menu(siteid){

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
    $('#site-list').html('');
    var sites = '';
    var site_head = '';
    $.ajax({
        type: 'get',
        url: '/client/site/api/',
        data: {},
        success: function(data) {
            if (data.status) {
                $.each(data.data, function (i, item) {                   

                    if(siteid == item.id){
                        site_head = '<a class="dropdown-toggle count-info" data-toggle="dropdown" href="#" aria-expanded="true"><strong class="font-bold">'+item.name+'</strong><b class="caret"></b></a>';

                    }
                    else{
                        sites = sites + '<li><a href="/admin/site/'+item.id+'">'+item.name+'</a></li>';
                    }

                });
                if(siteid == 0){

                    site_head = '<a class="dropdown-toggle count-info" data-toggle="dropdown" href="#" aria-expanded="true"><strong class="font-bold">Dashboard</strong><b class="caret"></b></a>';

                }
                else{

                    sites = sites+ '<li><a href="/admin/">Dashboard</a></li>';

                }
                site_list_html = site_head+'<ul class="dropdown-menu animated fadeInRight m-t-xs" >'+sites+'<li class="divider"></li>';
                if (data.sites_available > 0 ){
                    site_list_html = site_list_html +'<li><div class="text-center link-block">\
                                    <a href="#" id="wifisitemodal-add-new"><strong>Add New Site</strong><i class="fa fa-angle-right"></i></a></div></li>';
                }
                site_list_html = site_list_html +'</ul>';
                $('#site-list').html(site_list_html);
            }
            else{
                    toastr.options= toastr_options;
                    var $toast = toastr['error']("ERROR", data.msg);               
            }
        }
    });

}
function resetformfields(formid) {
        $('#'+formid).find('input:text, input:password, input:file, select, textarea').val('');
        $('#'+formid).find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected')
    
    }

function create_client_site_menu(siteid){

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
    $('#site-list').html('');
    var sites = '';
    var site_head = '';
    $.ajax({
        type: 'get',
        url: '/client/site/api/',
        data: {},
        success: function(data) {
            if (data.status) {
                $.each(data.data, function (i, item) {                   

                    if(siteid == item.id){
                        site_head = '<a class="dropdown-toggle count-info" data-toggle="dropdown" href="#" aria-expanded="true"><strong class="font-bold">'+item.name+'</strong><b class="caret"></b></a>';

                    }
                    else{
                        sites = sites + '<li><a href="/client/'+item.id+'">'+item.name+'</a></li>';
                    }

                });
                site_list_html = site_head+'<ul class="dropdown-menu animated fadeInRight m-t-xs" >'+sites+'<li class="divider"></li></ul>';


                $('#site-list').html(site_list_html);
            }
            else{
                    toastr.options= toastr_options;
                    var $toast = toastr['error']("ERROR", data.msg);               
            }
        }
    });

}    