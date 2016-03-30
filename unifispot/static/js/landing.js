

var FilesUpload = function(file_elementid,url,file_form_id,form_id) {

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
        $.ajaxSetup({
            type: 'POST',
            timeout: 30000,
            error: function(xhr) {
                    $.unblockUI();
                    toastr.options= toastr_options;
                    var $toast = toastr['error']("ERROR", "Network timeout!!,Please try again later");
                 }
         });    
    function redraw_images(){
        var $iframe = $("#preview-iframe").contents();
        var logofile = $('#landingpageform #logofile').val();
        var bgfile = $('#landingpageform #bgfile').val();
        var tosfile = $('#landingpageform #tosfile').val();

        $iframe.find('.client-logo img').attr('src',logofile);
        $iframe.find('#agreetos a').attr('href',tosfile);
        $iframe.find('html').css('background-image','url('+bgfile+')');

    };

    $('#remove-'+file_elementid).click(function(e) {
        $('#'+form_id+' #'+file_form_id).val('');
        redraw_images();
    });


    $('#'+file_elementid).val('');
     $('#'+file_elementid).fileupload({
        url: url,
        sequentialUploads: true,     
        add: function (e, data) {
            $.blockUI();
            data.submit();
        },
        start: function (e, data) {
            $.blockUI();           
        },
        finish: function (e, data) {
            $.unblockUI();          
        },     
        error: function (e, data) {
            $.unblockUI();
            toastr.options= toastr_options;
            var $toast = toastr['error']("ERROR", 'Some error occured while uploading the file');
        }, 
        success: function (e, data) {
            $.unblockUI();
            if(e.status){
                toastr.options= toastr_options;
                var $toast = toastr['success']("Success", e.msg);
                $('#'+form_id+' #'+file_form_id).val(e.singleitem.file_location);
                redraw_images();

            }else{
                toastr.options= toastr_options;
                var $toast = toastr['error']("ERROR", e.msg);

            }           
        }            
    });
   

};

function repopulate_landingpage(){
    var pagebgcolor = $('#simplelandingpageform #pagebgcolor1').val()
    var gridbgcolor = $('#simplelandingpageform #gridbgcolor').val()
    var textcolor = $('#simplelandingpageform #textcolor').val()
    var textfont = $('#simplelandingpageform #textfont').val()

    $('#landingpageform #pagebgcolor').val(pagebgcolor);
    $('#landingpageform #bgcolor').val(gridbgcolor);
    $('#landingpageform #topbgcolor').val(gridbgcolor);
    $('#landingpageform #toptextcolor').val(textcolor);
    $('#landingpageform #topfont ').val(textfont);
    $('#landingpageform #middlebgcolor').val(gridbgcolor);
    $('#landingpageform #middletextcolor').val(textcolor);
    $('#landingpageform #middlefont ').val(textfont);
    $('#landingpageform #bottombgcolor').val(gridbgcolor);
    $('#landingpageform #bottomtextcolor').val(textcolor);
    $('#landingpageform #bottomfont ').val(textfont);
    $('#landingpageform #footerbgcolor').val(gridbgcolor);
    $('#landingpageform #footertextcolor').val(textcolor);
    $('#landingpageform #footerfont ').val(textfont);
    $('#landingpageform #btnbgcolor').val(gridbgcolor);
    $('#landingpageform #btnlinecolor').val(textcolor);
    $('#landingpageform #btntxtcolor').val(textcolor);


};

function redraw_preview(){
    var $iframe = $("#preview-iframe").contents();
    var logofile = $('#landingpageform #logofile').val();
    var bgfile = $('#landingpageform #bgfile').val();
    var tosfile = $('#landingpageform #tosfile').val();

    var bgcolor = $('#landingpageform #bgcolor').val();
    var base_font = $('#landingpageform #base_font option:selected').text();

    var pagebgcolor = $('#landingpageform #pagebgcolor').val();
    var topbgcolor = $('#landingpageform #topbgcolor').val();
    var toptextcolor = $('#landingpageform #toptextcolor').val();
    var topfont = $('#landingpageform #topfont option:selected').text();
    var middlebgcolor = $('#landingpageform #middlebgcolor').val();
    var middletextcolor = $('#landingpageform #middletextcolor').val();
    var middlefont = $('#landingpageform #middlefont option:selected').text();
    var bottombgcolor = $('#landingpageform #bottombgcolor').val();
    var bottomtextcolor = $('#landingpageform #bottomtextcolor').val();
    var bottomfont = $('#landingpageform #bottomfont option:selected').text();
    var footerbgcolor = $('#landingpageform #footerbgcolor').val();
    var footertextcolor = $('#landingpageform #footertextcolor').val();
    var footerfont = $('#landingpageform #footerfont option:selected').text();
    var btnbgcolor = $('#landingpageform #btnbgcolor').val();
    var btnlinecolor = $('#landingpageform #btnlinecolor').val();
    var btntxtcolor = $('#landingpageform #btntxtcolor').val();


    $iframe.find('.client-logo img').attr('src',logofile);
    $iframe.find('#agreetos a').attr('href',tosfile);
    $iframe.find('html').css('background-color',pagebgcolor);
    $iframe.find('html').css('background-image','url('+bgfile+')');

    $iframe.find('.row-header').css('background-color',bgcolor);
    $iframe.find('.row-header').css('font-family',base_font);

    $iframe.find('.row-top-content').css('background-color',topbgcolor);
    $iframe.find('.row-top-content').css('font-family',topfont);
    $iframe.find('.row-top-content').css('color',toptextcolor);

    $iframe.find('.row-middle-content').css('background-color',middlebgcolor);
    $iframe.find('.row-middle-content').css('font-family',middlefont);
    $iframe.find('.row-middle-content').css('color',middletextcolor);

    $iframe.find('.input-guest').css('background-color',middlebgcolor);
    $iframe.find('.input-guest').css('font-family',middlefont);
    $iframe.find('.input-guest').css('color',middletextcolor);
    $iframe.find('.input-guest').css('border-color',middletextcolor);

    $iframe.find('.row-bottom').css('background-color',bottombgcolor);
    $iframe.find('.row-bottom').css('font-family',bottomfont);
    $iframe.find('.row-bottom').css('color',bottomtextcolor);

    $iframe.find('.row-bottom a').css('font-family',bottomfont);
    $iframe.find('.row-bottom a').css('color',bottomtextcolor);

    $iframe.find('.row-footer').css('background-color',footerbgcolor);
    $iframe.find('.row-footer').css('font-family',footerfont);
    $iframe.find('.row-footer').css('color',footertextcolor);

    $iframe.find('.btn-guest').css('background-color',btnbgcolor);
    $iframe.find('.btn-guest').css('border-color',btnlinecolor);
    $iframe.find('.btn-guest').css('font-family',bottomfont);
    $iframe.find('.btn-guest').css('color',btntxtcolor);


};


