def get_elements(browser,url,page_elements):       
    '''Get a page and return a bit map showing if elements specified by page_elements exists or not'''
    result  = {}
    browser.get(url)
    for ele in page_elements:
        result[ele]  = None
        try:
            element = browser.find_element_by_id(ele)
        except:
            pass
        else:
            result[ele] = 1
    return result


def login_new(browser,url,cred):       
    '''Login to the given URL using credentials provided'''
    result  = {}
    browser.get(url)
    for ele in page_elements:
        result[ele]  = None
        try:
            element = browser.find_element_by_id(ele)
        except:
            pass
        else:
            result[ele] = 1
    return result



