from flask.views import MethodView
from flask import render_template,jsonify
from unifispot.models import db,User,user_datastore,Role
from sqlalchemy.exc import IntegrityError
#from networkhq.signup import user_datastore, security
from .forms import UserForm

class UserAPI(MethodView):

    def get_template_name(self):
        return None

    def get_modal_obj(self):
        return User()

    def get_form_obj(self):
        return UserForm()

    def api_path(self):
        return None


    def get(self, id):
        if id != 1:
            return jsonify({'status': 0,'msg':'Not Allowed'})
            
        else:
        #Returns a single element
            singleitem = self.get_modal_obj().query.filter_by(id=id).first()
            if singleitem:
                return jsonify({'status':1,'singleitem':singleitem.to_dict()})
            else:
                return jsonify({'status':0})
           

    def post(self,id):
        if id != 1:
            return jsonify({'status': 0,'msg':'Not Allowed'})
        else:
            # update a single item
            singleitem = self.get_modal_obj().query.filter_by(id=id).first()
            if singleitem:
                form1 = self.get_form_obj()
                form1.populate()
                if form1.validate_on_submit():
                    singleitem.populate_from_form(form1)
                    try:
                        db.session.commit()
                    except IntegrityError:
                        return jsonify({'status': None,'msg':'Value already exists in the database'})
                    return jsonify({'status': 1})
                else:
                    print  form1.errors
                    return jsonify({'status':0,'msg': form1.errors})
            return jsonify({'status':0,'msg': 'unknown user'})


    def delete(self, id):
            # delete a single item
        singleitem = self.get_modal_obj().query.filter_by(id=id).first()

        if singleitem:
            db.session.delete(singleitem)
            db.session.commit()
            return jsonify({'status':1})
        else:
            return jsonify({'status':0})



