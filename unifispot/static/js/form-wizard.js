
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
        var resetformfields = function(formid) {
                $('#'+formid).find('input:text, input:password, input:file, select, textarea').val('');
                $('#'+formid).find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected')
            
            }
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
        var wifiform_steps = {
                bodyTag: "fieldset",
                onStepChanging: function (event, currentIndex, newIndex)
                {
                    // Always allow going backward even if the current step contains invalid fields!
                    if (currentIndex > newIndex)
                    {
                        return true;
                    }

                    // Forbid suppressing "Warning" step if the user is to young
                    if (newIndex === 3 && Number($("#age").val()) < 18)
                    {
                        return false;
                    }

                    var form = $(this);

                    // Clean up if user went backward before
                    if (currentIndex < newIndex)
                    {
                        // To remove error styles
                        $(".body:eq(" + newIndex + ") label.error", form).remove();
                        $(".body:eq(" + newIndex + ") .error", form).removeClass("error");
                    }

                    // Disable validation on fields that are disabled or hidden.
                    form.validate().settings.ignore = ":disabled,:hidden";

                    // Start validation; Prevent going forward if false
                    return form.valid();
                },
                onStepChanged: function (event, currentIndex, priorIndex)
                {
                    // Suppress (skip) "Warning" step if the user is old enough.
                    if (currentIndex === 2 && Number($("#age").val()) >= 18)
                    {
                        $(this).steps("next");
                    }

                    // Suppress (skip) "Warning" step if the user is old enough and wants to the previous step.
                    if (currentIndex === 2 && priorIndex === 3)
                    {
                        $(this).steps("previous");
                    }
                },
                onFinishing: function (event, currentIndex)
                {
                    var form = $(this);

                    // Disable validation on fields that are disabled.
                    // At this point it's recommended to do an overall check (mean ignoring only disabled fields)
                    form.validate().settings.ignore = ":disabled";

                    // Start validation; Prevent form submission if false
                    return form.valid();
                },
                onCanceled: function (event)
                {
                        $('#wifisitemodal').modal('hide');
                        formid("wifisitemodal-form");


                },                
                onFinished: function (event, currentIndex)
                {
                    var form = $(this);

                    // Submit form input
                    url = $( "#wifisitemodal-form" ).attr( 'action' );
                    $.ajaxSetup({
                        type: 'POST',
                        timeout: 30000,
                        error: function(xhr) {
                                $.unblockUI("#wifisitemodal-form");
                                toastr.options= toastr_options;
                                var $toast = toastr['error']("ERROR", "Network timeout!!,Please try again later");
                             }
                     });
                    //block UI while form is processed
                    $.blockUI({target: "#wifisitemodal-form"});
                    //$('#'+modal).modal('hide');
                    $.post(url, $( "#wifisitemodal-form" ).serialize(),function(data) {

                            $.unblockUI("#wifisitemodal-form");
                            if(data.status){
                                toastr.options= toastr_options;
                                var $toast = toastr['success']("Success", data.msg);
                                $('#wifisitemodal').modal('hide');
                                location.reload();    
                            }
                            else{
                                toastr.options= toastr_options;
                                var $toast = toastr['error']("ERROR", data.msg);
  
                            }
                        },
                        'json'// I expect a JSON response
                    );
                }
            }
        var wifiform_validate ={
                        errorPlacement: function (error, element)
                        {
                            element.before(error);
                        },
                        rules: {
                            redirect_url: {
                                url:true,
                                required:{
                                    depends:function(element) {
                                        return $('#wifisitemodal-form #redirect_method option:selected').val()  == 2;
                                    }
                                 }  
                            },   
                            fb_page: {
                                url:true,
                                required:{
                                    depends:function(element) {
                                        return $('#wifisitemodal-form #auth_method option:selected').val()  == 5;
                                    }
                                 }  
                            },
                            fb_app_secret: {
                                required:{
                                    depends:function(element) {
                                        return $('#wifisitemodal-form #auth_method option:selected').val()  == 5;
                                    }
                                 }  
                            },
                            fb_appid: {
                                required:{
                                    depends:function(element) {
                                        return $('#wifisitemodal-form #auth_method option:selected').val()  == 5;
                                    }
                                 }  
                            }  ,
                            get_email: {
                                required:{
                                    depends:function(element) {
                                        return $('#wifisitemodal-form #auth_method option:selected').val()  == 3;
                                    }
                                 }  
                            }                               

                        },
                        messages: {
                            redirect_url: {
                              required: "Please Enter a Valid URL including http:// or https://"
                            },         
                            fb_page: {
                              required: "Please Enter a Valid URL including http:// or https://"
                            },
                            get_email: {
                              required: "Please select atleast Email field for EMail Authentication"
                            }                                 
                      }
                    }

        $(document).ready(function(){       


            $("#wifisitemodal-form").steps(wifiform_steps).validate(wifiform_validate);
       });