
from flask import current_app

def check_view_anonymous_user_not_allowed(url):
    '''Check if the given VIEW is not accessable by a Anonymous(not logged in) User

    '''
    result = current_app.test_client().get(url,follow_redirects=True)    
    assert 'Login in. To see it in action' in result.data, 'Anonymous user not getting login page while trying to View URL:%s'%url    


def check_view_user_type_not_allowed(url):
    '''Check if the given VIEW is not accessable by  User currently logged in 

    '''
    result = current_app.test_client.get(url,follow_redirects=True)    
    assert '401 UNAUTHORIZED' == result.status, 'Current user not getting 401 UNAUTHORIZED while trying to View URL:%s'%url    


def check_view_user_type_allowed(url,content =None):
    '''Check if the given VIEW is accessable by  User currently logged in and optionally check if the body has given content

    '''
    result = current_app.test_client.get(url,follow_redirects=True)    
    assert '200 OK' == result.status, 'Current user  getting:%s instead of  200 OK while trying to View URL:%s'%(result.status,url)
    if content:
        assert content in result.data, 'Given content:%s not found in data received from URL:%s'%(content,url)

def check_view_user_401(url):
    '''Check if the given VIEW is access by  User produces 401 UNAUTHORIZED

    '''
    result = current_app.test_client.get(url,follow_redirects=True)    
    assert '401 UNAUTHORIZED' == result.status, 'Current user  getting:%s instead of  401 UNAUTHORIZED while trying to View URL:%s'%(result.status,url)    

def check_view_user_404(url):
    '''Check if the given VIEW is access by  User produces 404 NOT FOUND

    '''
    result = current_app.test_client.get(url,follow_redirects=True)    
    assert '404 NOT FOUND' == result.status, 'Current user  getting:%s instead of  401 UNAUTHORIZED while trying to View URL:%s'%(result.status,url)        