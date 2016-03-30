import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequestKeyError
from flask import render_template,jsonify,request,url_for,current_app,send_from_directory
import time
from PIL import Image
from magic import Magic
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from unifispot.extensions import db
from unifispot.base.utils.forms import print_errors,get_errors

import random
import time
import string


FILE_TYPE_UNKNOWN   = 1
FILE_TYPE_IMAGE     = 2
FILE_TYPE_PDF       = 3
FILE_TYPE_DOC       = 4

class FileAPI(MethodView):

    def __init__(self):
        self.upload_folder = None    
        self.allowed_files = [FILE_TYPE_IMAGE,FILE_TYPE_PDF]  
        self.entity_name   = "File"  

    def get_modal_obj(self):
        raise NotImplementedError

    def get_form_obj(self):
        raise NotImplementedError


    def handleUpload(self,file,thumbsize=32):
        """ Generic handler for uploading file, Need to pass app context and file
            Based on https://bitbucket.org/adampetrovic/flask-uploader/
            And http://stackoverflow.com/questions/17584328/any-current-examples-using-flask-and-jquery-file-upload-by-blueimp

        """
        if not file:
            return None
        else :
            filename = time.strftime('%Y%m%d-%H%M%S') + '-' + self.filename_gen(file.filename)
            full_file_name = os.path.join(self.base_folder,self.upload_folder, filename)
            file.save(full_file_name)
            rel_filepath = '/static/'+self.upload_folder +'/'+ filename
            #upload to S3
            self.push_file_to_s3(full_file_name,rel_filepath)
            if current_app.config['UPLOAD_TO_S3']:
                filetype = self.check_file_typ(filename)
            if filetype == FILE_TYPE_IMAGE: 
                pass         
                #self.generate_and_save_thumbnail(filename,thumbsize=256)      
                #thumbname = '/static/'+self.upload_folder+'/thumbs/'+filename
            elif filetype == FILE_TYPE_PDF:
                thumbname = '/static/img/pdf-icon.jpg'
            else:
                #unknown file,delete file and return none
                #TODO---Add code to handle file deletion
                return None       
            return {'filename':rel_filepath,'filetype':filetype,'thumbname':''}

    def push_file_to_s3(self,full_file_name,rel_filepath):
        try:
            import boto
            from boto.s3.key import Key
            bucket_name = current_app.config['S3_BUCKET']
            # connect to the bucket
            conn = boto.connect_s3(current_app.config['S3_ACCESS_KEY'],
                            current_app.config['S3_SECRET_KEY'],host=current_app.config['S3_ENDPOINT'])
            bucket = conn.get_bucket(bucket_name)
            # go through each version of the file
            key = rel_filepath
            # create a key to keep track of our file in the storage 
            k = Key(bucket)
            k.key = key
            k.set_contents_from_filename(full_file_name)
            # we need to make it public so it can be accessed publicly
            # using a URL like http://s3.amazonaws.com/bucket_name/key
            k.make_public()
            # remove the file from the web server
            #os.remove(full_file_name)
        except:
            current_app.logger.exception('exception while trying to upload file')

    def generate_and_save_thumbnail(self, filename,thumbsize):
        myimage = Image.open(os.path.join(self.base_folder,self.upload_folder, filename))
        (width, height) = myimage.size
        if width > thumbsize and height > thumbsize:
            print "RESIZING"
            myimage = myimage.resize((thumbsize,thumbsize ), Image.ANTIALIAS)
        full_thumb_name = os.path.join(self.base_folder,self.upload_folder, 'thumbs', filename)
        myimage.save(full_thumb_name)
        return filename

    def filename_gen(self,filename,size=6, chars=string.ascii_uppercase + string.digits):
        #get file extension if exists and add to the randomly generated filename
        file_extension = ''
        if '.' in filename:
            file_extension = '.'+filename.rsplit('.', 1)[1]
        fname= ''.join(random.choice(chars) for _ in range(size))
        return fname + file_extension

    def check_file_typ(self,filename):
        full_file_name = os.path.join(self.base_folder,self.upload_folder, filename)
        if os.name == 'nt':
            #if its windows we need to specify magic file explicitly
            #https://github.com/ahupp/python-magic#dependencies
            magic = Magic(magic_file=current_app.config['MAGIC_FILE_WIN32'],mime=True)
        else:
            magic = Magic(mime=True)
        try:
            file_type = magic.from_file(full_file_name)
        except IOError:
            app.logger.error("check_file_type is called with non existing file or I/O error while opening :%s"%full_file_name)
            return None
        if file_type == 'image/gif':
            return FILE_TYPE_IMAGE    
        elif file_type == 'image/png':
            return FILE_TYPE_IMAGE
        elif file_type == 'image/jpeg':
            return FILE_TYPE_IMAGE
        elif file_type == 'application/pdf':
            return FILE_TYPE_PDF
        else:
            return FILE_TYPE_UNKNOWN        

    def get(self, id):
        if id is None:
            # return no file ID specified for download  
            return jsonify({'status':0,'msg':'Invalid ID Specified for the File '})
        filetodownload = self.get_modal_obj().query.filter_by(id=id).first()
        if not filetodownload:
            #return None
            current_app.logger.debug("Invalid File ID specified")
            return jsonify({'status':0,'msg':'Invalid File ID Specified  '})
        else:
            return jsonify({'status':1,'singleitem':filetodownload.to_dict(),'msg':'Successfully returning files '})

    def post(self,id):
        if id is None:
            #upload new file
            try:
                try:
                    upload_file = request.files['logofile']
                except BadRequestKeyError:
                    try:
                        upload_file = request.files['bgfile']
                    except BadRequestKeyError:
                        try:
                            upload_file = request.files['tosfile']
                        except BadRequestKeyError:
                            return jsonify({'status': '0','msg':'Unknown file!! only logofile,bgfile and tosfile are allowed'})
                if upload_file:
                    filetoupload = self.handleUpload(upload_file)   
                    if not filetoupload  :
                        return jsonify({'status': '0','msg':'Error Occured While trying to upload file'})
                    newfile = self.get_modal_obj()
                    newfile.file_location   = filetoupload['filename']
                    newfile.file_type       = filetoupload['filetype']
                    newfile.file_thumb_location = filetoupload['thumbname']
                    newfile.file_label = secure_filename(upload_file.filename)
                    #update ownership data for this file like siteid,clientid etc
                    newfile.update_ownership(request)
                    try:
                        db.session.add(newfile)
                        db.session.commit()
                    except IntegrityError:
                        return jsonify({'status': None,'msg':'Value already exists in the database for this file '})
                    else:
                        return jsonify({'status': 1,'singleitem':newfile.to_dict(),'msg':'Added New Entry for:File into Database'})
            except:
                current_app.logger.exception("Fileupload exception")
                return jsonify({'status': '0','msg':'Error Occured While trying to upload file'})
        else:
        # update a single item
            singleitem = self.get_modal_obj().query.filter_by(id=id).first()
            if singleitem and request.form['file_label']:
                singleitem.file_label = request.form['file_label']
                try:
                    db.session.commit()
                except IntegrityError:
                    return jsonify({'status': None,'msg':'Value already exists in the database for:File'})
                else:
                    return jsonify({'status': 1,'msg':'Updated File Details'})
            return jsonify({'status':0,'err': 'Some Error Occured while processing: File'})

    def delete(self, id):
        # delete a single item
        singleitem = self.get_modal_obj().query.filter_by(id=id).first()
        if singleitem:
            #TODO ---add code to delete file from file system!
            db.session.delete(singleitem)
            db.session.commit()
            return jsonify({'status':1,'msg':'Deleted Entry for File from Database'})
        else:
            return jsonify({'status':0,'msg':'Unknown ID specified for  '})            



