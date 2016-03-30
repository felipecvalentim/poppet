from flask.ext.wtf import Form
from wtforms import TextField, HiddenField,SelectField,FileField,BooleanField,PasswordField,TextAreaField,RadioField,SelectMultipleField,widgets,validators
from wtforms.validators import Required
from timezones import zones
from unifispot.const import ACCOUNT_TYPE_FREE,ACCOUNT_TYPE_SILVER,ACCOUNT_TYPE_GOLD,ACCOUNT_TYPE_GOLD_PREM
import arrow
from .models import Account

class AccountForm(Form):
    name                    = TextField('Account Name',validators = [Required()])  
    sites_allowed           = TextField('Sites Allowed',validators = [Required()],default='1')
    account_type            = SelectField('Account Type',coerce=int,choices=[],default=ACCOUNT_TYPE_FREE)    
    expiresat               = TextField('Expires At',validators = [Required()],default=arrow.utcnow().replace(days=7).datetime)
    unifi_server            = TextField('Controller Host',validators = [Required()],default="127.0.0.1")   
    unifi_server_ip         = TextField('Controller IP',validators = [Required()],default="127.0.0.1")   
    unifi_user              = TextField('Unifi Login',validators = [Required()],default="ubnt")   
    unifi_pass              = PasswordField('Unifi Password',validators = [Required()],default="ubnt")  
    en_api_export           = BooleanField('API Export',default=0)
    en_reporting            = BooleanField('Reporting',default=0)
    en_analytics            = BooleanField('Analytics',default=0)
    en_advertisement        = BooleanField('Advertisement',default=0)
    en_footer_change        = BooleanField('Footer Display',default=0)
    en_fbauth_change        = BooleanField('FB Own APP',default=0)
    logins_allowed          = TextField('Monthly Logins Allowed')


    def populate(self):
        self.account_type.choices = [(ACCOUNT_TYPE_FREE,'Free'),(ACCOUNT_TYPE_SILVER,'Silver'),(ACCOUNT_TYPE_GOLD,'Gold'),(ACCOUNT_TYPE_GOLD_PREM,'Gold Premium')]

class UserForm(Form):
    email       = TextField('Email',validators = [Required()])
    displayname = TextField('Name',validators = [Required()])
    password    = PasswordField('Password') 
    repassword  = PasswordField('Confirm Password')
    
    def populate(self):
        pass

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.password and (self.password.data != self.repassword.data):
            self.password.errors.append("Entered passwords didn't match")
            return False
        return True

class AdminForm(Form):
    email       = TextField('Email',validators = [Required()])
    displayname = TextField('Name',validators = [Required()])
    password    = PasswordField('Password') 
    repassword  = PasswordField('Confirm Password')
    account     = SelectField('Account',coerce=int,choices=[])  
    
    def populate(self):
        accounts = Account.query.all()
        self.account.choices = []
        for account in accounts:
            self.account.choices.append((account.id,account.name))

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.password and (self.password.data != self.repassword.data):
            self.password.errors.append("Entered passwords didn't match")
            return False
        return True