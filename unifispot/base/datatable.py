from flask import request

class DataTablesServer(object):
 
    def __init__( self, request, columns, index,db,model,modal_filters=None):
        self.columns = columns
        self.index = index
        self.model = model
        #Flask-sqlalchemy db object
        self.db = db
        # values specified by the datatable for filtering, sorting, paging
        self.request_values = request.values  
        # Extra filters to be givcen to run_queries
        self.modal_filters = modal_filters       
        # results from the db
        self.result_data = []         
        # total in the table after filtering
        self.cardinality_filtered = 0 
        # total in the table unfiltered
        self.cardinality = 0    
        self.run_queries()

        
    def custom_column(self,row):
        #function to add custom column if needed
        button_row = '''<a class="btn btn-red btn-sm delete" href="#" id="%s" alt="Delete">
                        <i class="fa fa-times"></i>Delete</a>'''%(row['id'])
        button_row += '''<a class="btn  btn-sm edit" href="#" id="%s" alt="Edit">
                        <i class="fa fa-pencil"></i>Edit</a>'''%(row['id'])
        return button_row
    
    def output_result(self):                
        output = {}
        output['draw'] = int(self.request_values.get('draw',1))
        output['recordsTotal'] = int(self.cardinality)
        output['recordsFiltered'] = int(self.cardinality_filtered)
        aaData_rows = [] 
        for row in self.result_data:
            aaData_row = []
            for i in range( len(self.columns) ): 
                aaData_row.append(row[ self.columns[i] ])             
            # add additional rows here that are not represented in the database
            # aaData_row.append(('''<input id='%s' type='checkbox'></input>''' % (str(row[ self.index ]))).replace('\\', ''))            
            custom_col = self.custom_column(row)
            if custom_col:
                aaData_row.append(custom_col)
            aaData_rows.append(aaData_row)
                
 
        output['data'] = aaData_rows
 
        return output

    def run_queries(self): 
        # pages has 'start' and 'length' attributes
        pages = self.paging()
        # the term you entered into the datatable search
        _filter = self.filtering()
        # the document field you chose to sort
        sorting = self.sorting()        
        modal_inst = self.model 
        #iserv_query = Server.query.offset(pages['start']).limit(pages['length']).all()
        results =  self.model.search_query(term=_filter,offset=pages['start'],limit=pages['length'],sort=sorting,modal_filters=self.modal_filters)
        #self.result_data = [ x.to_dict() for x in iserv_query]
        count = 0
        for en in results['results']:
            count = count + 1
            self.result_data.append(en.to_table_row())
        self.cardinality_filtered = results['total']
        self.cardinality= results['total']	

    def filtering(self):
         
        # build your filter spec
        _filter = ""
        if ( self.request_values.has_key('search[value]') ) and ( self.request_values.get('search[value]') ):
            _filter = self.request_values['search[value]']	           
        return _filter
        
    def sorting(self):
                
        order = { 'order':'acs','column':'0' }
        # mongo translation for sorting order
        if (  self.request_values.get('order[0][dir]')   and self.request_values.get('order[0][column]')    ):            
            order = { 'order':self.request_values['order[0][dir]'],'column': self.request_values['order[0][column]'] }
        return order
 
    def paging(self):
        pages ={ 'start':0, 'length':10 }
        if (self.request_values.get('start') ) and (self.request_values.get('length') ):
            pages['start'] = int(self.request_values['start'])
            pages['length'] = int(self.request_values['length'])
        
        return pages
