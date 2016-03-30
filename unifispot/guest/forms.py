from flask.ext.wtf import Form
from wtforms import TextField, HiddenField
from wtforms.validators import Required,DataRequired,Email

from unifispot.const import *

class FacebookTrackForm(Form):

    authlike = HiddenField("Auth Like")
    authpost = HiddenField("Auth Post")

def generate_emailform(form_fields):
    class F(Form):
        pass
    setattr(F, 'email', TextField('Email ID',validators = [DataRequired(),Email()]))
    if form_fields &  FORM_FIELD_FIRSTNAME :
         setattr(F, 'firstname', TextField('First Name',validators = [Required()])) 
    if form_fields &  FORM_FIELD_LASTNAME :
         setattr(F, 'lastname', TextField('Last Name',validators = [Required()])) 
    if form_fields &  FORM_FIELD_PHONE :
         setattr(F, 'phonenumber', TextField('Phone Number',validators = [Required()]))                   
    return F()

def generate_voucherform(form_fields):
    class F(Form):
        pass
    setattr(F, 'voucher', TextField('Voucher',validators = [Required()]))   
    if form_fields &  FORM_FIELD_FIRSTNAME :
         setattr(F, 'firstname', TextField('First Name',validators = [Required()])) 
    if form_fields &  FORM_FIELD_LASTNAME :
         setattr(F, 'lastname', TextField('Last Name',validators = [Required()])) 
    if form_fields &  FORM_FIELD_EMAIL :
         setattr(F, 'email', TextField('Email ID',validators = [DataRequired(),Email()]))
    if form_fields &  FORM_FIELD_PHONE :
         setattr(F, 'phonenumber', TextField('Phone Number',validators = [Required()]))   
    return F()

def generate_smsform(form_fields):
    class F(Form):
        pass
    setattr(F, 'phonenumber', TextField('Phone Number',validators = [Required()])) 
    if form_fields &  FORM_FIELD_FIRSTNAME :
         setattr(F, 'firstname', TextField('First Name',validators = [Required()])) 
    if form_fields &  FORM_FIELD_LASTNAME :
         setattr(F, 'lastname', TextField('Last Name',validators = [Required()])) 
    if form_fields &  FORM_FIELD_EMAIL :
         setattr(F, 'email', TextField('Email ID',validators = [DataRequired(),Email()]))
    return F()