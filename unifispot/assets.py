from flask.ext.assets import Bundle

bundles = {


    'global_css': Bundle(
        'css/bootstrap.min.css',
        'font-awesome/css/font-awesome.css',
        #'css/animate.css',
        'css/style.css',
        'css/plugins/toastr/toastr.min.css',
        output='gen/global.css'),
        
    'core_js': Bundle(
        'js/jquery-2.1.1.js',
        'js/bootstrap.min.js',
        'js/plugins/metisMenu/jquery.metisMenu.js',
        'js/plugins/slimscroll/jquery.slimscroll.min.js',
        'js/inspinia.js',
        'js/plugins/pace/pace.min.js',
        'js/plugins/toastr/toastr.min.js',
        'js/plugins/blockui/jquery.blockUI.js',
        'js/modal-form.js',
        'js/ajax-forms.js',
        output='gen/core.js'),

    'datatable_css': Bundle(
        'css/plugins/dataTables/dataTables.bootstrap.css',
        'css/plugins/dataTables/dataTables.responsive.css',
        'css/plugins/dataTables/dataTables.tableTools.min.css',
        output='gen/datatable.css'),

    'datatable_js': Bundle(
        'js/plugins/dataTables/jquery.dataTables.js',
        'js/plugins/dataTables/dataTables.bootstrap.js',
        'js/plugins/dataTables/dataTables.responsive.js',
        'js/plugins/dataTables/dataTables.tableTools.min.js',
        'js/plugins/bootbox/bootbox.min.js',
        'js/datatable.js',
        output='gen/datatable.js'),

    'landing_css': Bundle(
        'css/plugins/colorpicker/bootstrap-colorpicker.min.css',
        output='gen/landing.css'),    

    'landing_js': Bundle(
        'js/plugins/colorpicker/bootstrap-colorpicker.min.js',
        'js/landing.js',
        output='gen/landing.js'),        

    'wizard_css': Bundle(
        'css/plugins/steps/jquery.steps.css',
        output='gen/wizard.css'),    

    'wizard_js': Bundle(
        'js/plugins/steps/jquery.steps.min.js',
        'js/form-wizard.js',
        'js/plugins/validate/jquery.validate.min.js',
        output='gen/wizard.js'),  

    'fileupload_css': Bundle(
        'css/plugins/jquery-fileupload/jquery.fileupload.css',

        output='gen/fileupload.css'),    

    'fileupload_js': Bundle(
        'js/plugins/jquery-fileupload/vendor/jquery.ui.widget.js',
        'js/plugins/jquery-fileupload/jquery.iframe-transport.js',
        'js/plugins/jquery-fileupload/jquery.fileupload.js',
        output='gen/fileupload.js'),        

    'datepicker_css': Bundle(
        'css/plugins/datapicker/datepicker3.css',

        output='gen/datepicker.css'),    

    'datepicker_js': Bundle(
        'js/plugins/datapicker/bootstrap-datepicker.js',
        output='gen/datepicker.js'),    

}



