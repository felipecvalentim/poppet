from flask.ext.wtf import Form
from flask.ext.security import login_required,current_user
from wtforms import TextField, HiddenField,SelectField,FileField,BooleanField,PasswordField,TextAreaField,RadioField,SelectMultipleField,widgets,validators
from wtforms.validators import Required
from timezones import zones

from unifispot.const import AUTH_TYPE_BYPASS,AUTH_TYPE_SPLASH,AUTH_TYPE_EMAIL,AUTH_TYPE_VOUCHER,AUTH_TYPE_SOCIAL,AUTH_TYPE_SMS,API_END_POINT_NONE,API_END_POINT_MAIL_CHIMP
from unifispot.const import REDIRECT_ORIG_URL,REDIRECT_CUSTOM_URL,font_list,CLIENT_REPORT_NONE,CLIENT_REPORT_WEEKLY,CLIENT_REPORT_MONTHLY,ROLE_CLIENT


from .models import Sitefile,Wifisite,Landingpage,Client
from unifispot.models import User


        
class WifiSiteForm(Form):
    name            = TextField('Name',validators = [Required()])   
    timezone        = SelectField('Site Timezone',choices=[])
    unifi_id        = TextField('Unifi SiteID')
    enablehtml      = HiddenField('Enable HTML Landing Page')
    auth_fb         = BooleanField('Enable FB Login',default=1)
    auth_email      = BooleanField('Enable Email Login',default=1)
    auth_phone      = BooleanField('Enable Phone Login',default=1)
    auth_voucher    = BooleanField('Enable Voucher Login',default=1)
    fb_page         = TextField('Fb Page URL')
    auth_fb_like    = BooleanField('Ask For Page Like',default=1)
    auth_fb_post    = HiddenField('Ask Guest For Checkin')
    redirect_method = BooleanField('Redirect After Login',default=0)
    redirect_url    = TextField('Redirect URL')
    unifi_id        = TextField('UniFi Site ID')
    fb_app_secret   = TextField('FB APP Secret')
    fb_appid        = TextField('FB APP ID')
    reports_list    = TextField('Additional Report Recipients')
    reports_type    = SelectField('Select Reports Frequency',coerce=int,choices=[],default=CLIENT_REPORT_WEEKLY)
    client_id       = SelectField('Select Client',coerce=int,choices=[],default=0)
    template        = SelectField('Choose Template',choices=[],default='template1')
    get_firstname   = BooleanField('First Name',default=1)
    get_lastname    = BooleanField('Last Name',default=1)
    api_export      = SelectField('Select API End Point',coerce=int,choices=[],default=API_END_POINT_NONE)
    api_auth_field1 = TextField('API Auth Field1')
    api_auth_field2 = TextField('API Auth Field2')
    api_auth_field3 = TextField('API Auth Field3')


    def populate(self):        
        self.timezone.choices = [ (tz_name,tz_formated)for tz_offset, tz_name, tz_formated in zones.get_timezones() ]
        self.template.choices = [('template1','Template1'),('template2','Template2') ]
        self.reports_type.choices = [(CLIENT_REPORT_NONE,'No Reporting'),(CLIENT_REPORT_WEEKLY,'Weekly Reports'),(CLIENT_REPORT_MONTHLY,'Monthly Reports')]
        self.client_id.choices = []
        self.api_export.choices = [(API_END_POINT_NONE,'None'),(API_END_POINT_MAIL_CHIMP,'MailChimp')]
        for user in Client.query.filter_by(account_id=current_user.account_id).all():
            self.client_id.choices.append((user.id,user.displayname))


class LandingFilesForm(Form):
    logofile        = FileField('Logo File')
    bgfile          = FileField('Background Image')
    tosfile         = FileField('Select T&C pdf')

class SimpleLandingPageForm(Form):
    pagebgcolor1     = TextField('Page Background Color')
    gridbgcolor     = TextField('Grid Background Color')
    textcolor       = TextField('Text Color')
    textfont        = SelectField('Select Font',coerce=int,default=2)
    def populate(self):
        #Font options
        fonts = [(idx,font) for idx,font in enumerate(font_list)]
        self.textfont.choices = fonts

class LandingPageForm(Form):
    site_id         = HiddenField('Site ID')
    logofile        = HiddenField('Header File')  
    bgfile          = HiddenField('Background Image')
    pagebgcolor     = TextField('Page Background Color')    
    bgcolor         = TextField('Header Background Color')
    headerlink      = TextField('Header Link')
    basefont        = SelectField('Header Base Font',coerce=int,default=2)
    topbgcolor      = TextField('Top Background Color')
    toptextcolor    = TextField('Top Text Color')
    topfont         = SelectField('Top Font',coerce=int,default=2)
    toptextcont     = TextAreaField('Top Content')
    middlebgcolor   = TextField('Middle Background Color')
    middletextcolor = TextField('Middle Text Color')
    middlefont      = SelectField('Bottom Base Font',coerce=int,default=2)
    bottombgcolor   = TextField('Bottom Background Color')
    bottomtextcolor = TextField('Bottom Text Color')
    bottomfont      = SelectField('Base Font',coerce=int,default=2)
    footerbgcolor   = TextField('Footer Background Color')
    footertextcolor = TextField('Text Color')
    footerfont      = SelectField('Base Font',coerce=int,default=2)
    footertextcont  = TextAreaField('Footer Content')
    btnbgcolor      = TextField('Button Color')
    btntxtcolor     = TextField('Button Text Color')
    btnlinecolor    = TextField('Button Border Color')
    tosfile         = HiddenField('Select T&C pdf')
    copytextcont    = TextAreaField('Copyright Text')
    

    def populate(self,siteid):
        #Font options
        fonts = [(idx,font) for idx,font in enumerate(font_list)]
        self.basefont.choices = fonts
        self.topfont.choices = fonts
        self.middlefont.choices = fonts
        self.bottomfont.choices = fonts
        self.footerfont.choices = fonts
        self.site_id.data = siteid




class SiteFileForm(Form):
    file_label = TextField('File Label')

    def populate(self):
        pass 


class VoucherForm(Form):  
    duration        = TextField("Duration")
    notes           = TextField("Note")
    number          = TextField("Create")
    duration_t      = SelectField("Select",coerce=int,choices=[(1,'Hours'),(2,'Days'),(3,'Months')] )    
    def populate(self):
        pass