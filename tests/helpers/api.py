
from flask import current_app


def check_api_anonymous_user_not_allowed(url):
    '''Check if the given API is not accessable by a Anonymous(not logged in) User

        All 4 methods are checked to make sure login page is coming
    '''
    #GET
    result = current_app.test_client().get(url,follow_redirects=True)    
    assert 'Login in. To see it in action' in result.data, 'Anonymous user not getting login page while trying to call API URL:%s'%url
    #GET with ID =1
    result = current_app.test_client().get(url+'1',follow_redirects=True)    
    assert 'Login in. To see it in action' in result.data, 'Anonymous user not getting login page while trying to call API URL:%s'%url
    #POST
    result = current_app.test_client().post(url,follow_redirects=True)    
    assert 'Login in. To see it in action' in result.data, 'Anonymous user not getting login page while trying to call API URL:%s'%url
    #POST with ID=1
    result = current_app.test_client().post(url+'1',follow_redirects=True)    
    assert 'Login in. To see it in action' in result.data, 'Anonymous user not getting login page while trying to call API URL:%s'%url
    #DELETE with ID=1
    result = current_app.test_client().delete(url+'1',follow_redirects=True)    
    assert 'Login in. To see it in action' in result.data, 'Anonymous user not getting login page while trying to call API URL:%s'%url
    #DELETE
    result = current_app.test_client().delete(url,follow_redirects=True)    
    assert '405 METHOD NOT ALLOWED' == result.status, 'Anonymous user not getting login page while trying to call API URL:%s'%url


def check_api_user_type_not_allowed(url):
    '''Check if the given API is not accessable by a Special user_type

        All 4 methods are checked to make sure Not Authorized msg is coming
    '''    
    #GET
    result = current_app.test_client.get(url,follow_redirects=True).json   
    assert 0 == result['status'], 'Un allowed User not getting Status 0  while trying to call API URL:%s'%url
    assert 'Not Authorized' == result['msg'], 'Un allowed User not getting Not Authorized while trying to call API URL:%s'%url
    #GET with ID =1
    result = current_app.test_client.get(url+'1',follow_redirects=True).json     
    assert 0 == result['status'], 'Un allowed User not getting Status 0  while trying to call API  URL:%s'%url
    assert 'Not Authorized' == result['msg'], 'Un allowed User not getting Not Authorized while trying to call API URL:%s'%url
    #POST
    result = current_app.test_client.post(url,follow_redirects=True).json     
    assert 0 == result['status'], 'Un allowed User not getting Status 0  while trying to call API URL:%s'%url
    assert 'Not Authorized' == result['msg'], 'Un allowed User not getting Not Authorized while trying to call API URL:%s'%url
    #POST with ID=1
    result = current_app.test_client.post(url+'1',follow_redirects=True).json     
    assert 0 == result['status'], 'Un allowed User not getting Status 0  while trying to call API URL:%s'%url
    assert 'Not Authorized' == result['msg'], 'Un allowed User not getting Not Authorized while trying to call API URL:%s'%url
    #DELETE with ID=1
    result = current_app.test_client.delete(url+'1',follow_redirects=True).json     
    assert 0 == result['status'], 'Un allowed User not getting Status 0  while trying to call API URL:%s'%url
    assert 'Not Authorized' == result['msg'], 'Un allowed User not getting Not Authorized while trying to call API URL:%s'%url
    #DELETE
    result = current_app.test_client.delete(url,follow_redirects=True)     
    assert '405 METHOD NOT ALLOWED' == result.status, 'Un allowed User not getting 401 UNAUTHORIZED while trying to call API URL:%s'%url



def check_api_get(url,resp_dict=None):
    '''Run GET call on given API URL and compare result data to dictionary if provided

        Returns received data
    '''
    result = current_app.test_client.get(url,follow_redirects=True).json   
    assert 1 == result['status'], 'Status is not 1 when calling API get on :%s'%url
    if resp_dict:
        assert resp_dict == result['data'], 'Objects not matching while calling API get on :%s'%url 
    return result.get('data')


def check_api_get_datatable(url,num_results):
    '''Run GET call on given datatbale End Point

        Returns received data
    '''
    result = current_app.test_client.get(url,follow_redirects=True).json  
    assert num_results == result['recordsTotal'] , 'Incorrect recordsTotal value while calling datatble end point on :%s'%url



def check_api_get_error(url,msg=None):
    '''Run GET call on given API URL and check if given msg is thrown as error

        Returns received msg
    '''    
    result = current_app.test_client.get(url,follow_redirects=True).json   
    assert 0 == result['status'], 'Status is not 0 when calling API get on :%s'%url
    assert None != result.get('msg'), 'Status is 0 without giving any msg as error on :%s'%url    
    if msg:
        assert msg == result['msg'], 'Error msg:%s is not coming when calling API get on :%s'%(msg,url)
    return result.get('msg')

def check_api_post(url,obj_dict):
    '''Run POST on the given URL and check if status is 1

    '''
    result = current_app.test_client.post(url,follow_redirects=True,data=obj_dict).json   
    assert 1 == result['status'], 'Status is not 1 when calling API POST on :%s'%url
   

def check_api_post_error(url,obj_dict,msg=None):
    '''Run POST on the given URL and check if status is 0. Optinally compare error msg

        Returns error msg

    '''
    result = current_app.test_client.post(url,follow_redirects=True,data=obj_dict).json   
    assert 0 == result['status'], 'Status is not 0 when calling API POST with ERROR on :%s'%url
    assert None != result.get('msg'), 'Status is 0 without giving any msg as error on :%s'%url
    if msg:
        assert msg == result['msg'], 'Error msg:%s is not coming when calling API get on :%s'%(msg,url)
    return result.get('msg')


def check_api_post_mandatory_fields_check(url,fields,form):
    '''Run POST on the given URL and with empty object to check if all mandatory fields are checked and errors are shown


    '''
    result = current_app.test_client.post(url,follow_redirects=True,data={}).json   
    assert 0 == result['status'], 'Status is not 0 when calling API POST with ERROR on :%s'%url
    assert None != result.get('msg'), 'Status is 0 without giving any msg as error on :%s'%url
    msg = result.get('msg')
    #create form instance
    f =form()

    for field in fields:
        label = getattr(f,field).label.text
        assert 'Error in the %s field - This field is required'%label in msg, '%s is not mandatory while form submit'%label



def check_api_delete(url,msg=None):
    '''Run DELTE on the given URL and check if status is 1 Optinally check the msg

        Returns msg if any
    '''
    result = current_app.test_client.delete(url,follow_redirects=True).json   
    assert 1 == result['status'], 'Status is not 1 when calling API DELTE on :%s'%url
    assert None != result.get('msg'), 'Status is 0 without giving any msg as error on :%s'%url        
    if msg:
        assert msg == result['msg'], 'Error msg:%s is not coming when calling API get on :%s'%(msg,url)
    return result.get('msg')   

def check_api_delete_error(url,msg=None):
    '''Run DELETE on the given URL and check if status is 0. Optinally compare error msg

        Returns error msg

    '''
    result = current_app.test_client.delete(url,follow_redirects=True).json  
    assert 0 == result['status'], 'Status is not 1 when calling API DELETE on :%s'%url
    assert None != result.get('msg'), 'Status is 0 without giving any msg as error on :%s'%url    
    if msg:
        assert msg == result['msg'], 'Error msg:%s is not coming when calling API get on :%s'%(msg,url)
    return result.get('msg')