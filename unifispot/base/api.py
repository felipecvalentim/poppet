from flask.views import MethodView
from flask import render_template,jsonify,request
from sqlalchemy.exc import IntegrityError
from unifispot.base.datatable import DataTablesServer
from unifispot.base.utils.forms import print_errors,get_errors
from unifispot.extensions import db

class UnifispotAPI(MethodView):

    def __init__(self):
        self.columns = []
        self.index_column = "id"
        self.collection = "collection_name"
        self.entity_name    = ''

    def get_template_name(self):
        raise NotImplementedError

    def get_modal_obj(self):
        raise NotImplementedError

    def get_form_obj(self):
        raise NotImplementedError

    def api_path(self):
        raise NotImplementedError
        
    def datatable_obj(self,request,columns,index_column,db,modal_obj):
        raise NotImplementedError

    def get(self, id):
        if id is None:
            # return a list of all elements    
            results = self.datatable_obj(request, self.columns, self.index_column, db,self.get_modal_obj()).output_result()
            return jsonify(results) 
        else:
            #Returns a single element
            singleitem = self.get_modal_obj().query.filter_by(id=id).first()
            if singleitem:
                return jsonify({'status':1,'data':singleitem.to_dict(),'msg':'Successfully returning :%s'%self.entity_name})
            else:
                return jsonify({'status':0,'msg':'Invalid ID Specified for '%self.entity_name})
    def post(self,id):
        if id is None:
        # create a new element
            form1 = self.get_form_obj()
            form1.populate()
            if  form1.validate_on_submit():        
                newitem = self.get_modal_obj()
                newitem.populate_from_form(form1)
                try:
                    db.session.add(newitem)
                    db.session.commit()
                except IntegrityError:
                    return jsonify({'status': None,'msg':'Value already exists in the database for :%s'%self.entity_name})
                else:
                    return jsonify({'status': 1,'id':newitem.id,'msg':'Added New Entry for:%s into Database'%self.entity_name})
            else:
                print_errors(form1)
                return jsonify({'status':0,'msg': get_errors(form1)})

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
                        return jsonify({'status': None,'msg':'Value already exists in the database for:%s'%self.entity_name})
                    else:
                        return jsonify({'status': 1,'msg':'Updated :%s'%self.entity_name,'id':singleitem.id})
            else:
                return jsonify({'status':0,'msg': get_errors(form1)})
            return jsonify({'status':0,'err': 'Some Error Occured while processing:%s'%self.entity_name})
	

    def delete(self, id):
        # delete a single item
        singleitem = self.get_modal_obj().query.filter_by(id=id).first()
        if singleitem:
            db.session.delete(singleitem)
            db.session.commit()
            return jsonify({'status':1,'msg':'Deleted Entry:%s from Database'%self.entity_name})
        else:
            return jsonify({'status':0,'msg':'Unknown ID specified for:%s '%self.entity_name})



