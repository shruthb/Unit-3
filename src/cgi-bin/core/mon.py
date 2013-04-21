from pymongo import Connection

'''Create a new connection to a single MongoDB instance at host:port'''

connection=Connection()    #making a connection
db=connection.url_database  #getting a database
collection=db.url_collection #getting a collection


def formatdoc(ret_of_crawler):
    '''of the form 
    [{'url': url_string, 'features': list_of_features_which_are_true_for_that_website},{'url': '', 'features': ['camera', 'appcache']}]
    contains only features which are true for dat website '''
    li=[]                                                                                                
    for each in ret_of_crawler :
        dic={}
        dic["url"]=each["url"]
        fealist=[]                                                                                    
        for i in each:
            if each[i]==True:
                fealist.append(i)
        dic["features"]=fealist
        li.append(dic)                                                                                      
    #print li
    return li #ret_of_crawler[url]

def put(ret_of_crawler):
    '''formats the result of the crawler and inserts it into the database'''
    doc = formatdoc(ret_of_crawler)
    collection.insert(doc)

def needtocrawl(url):
    '''to keep note of urls for which website has been queried but we havent crawled yet'''
    collection.insert({"tocrawl":url})

def getres(url,feat):
    '''the result when url,features to check is given'''
    retdict={}
    res={}
    li=[]
    res.update({'url':url})
    retdict=collection.find_one({'url':url})
    if not retdict:
        return None
    #del retdict[u'_id']
    for each in retdict[u'features']:
        each=str(each)
        li.append(each)
    #print "features : ",li
    if type(feat) == str:
        feat = [feat]
    for i in feat:
        if i in li:
            res[i]=True
        else:
            res[i]=False
    #print 'result of'
    return res

def geturl(url):
    '''the result wen only url is specified in the query nd no features'''
    res = collection.find_one({'url':url})
    if not res:
        return None
    del res[u'_id']
    li=[]
    res["url"]=str(res["url"])
    for each in res["features"]:
        each=str(each)
        li.append(each)
    
    res["features"]=li
    return res

def formatit(dbobj):
    del dbobj[u'_id']
    new={}
    new["url"]=str(dbobj["url"])
    # new["features"]=str(d["features"])
    return new
    
def getfeat(find):
    '''the result when only features is specified - urls which have all these features'''
    ob = collection.find({"features": {"$all": find}}) # "$in"  => or
    res = []
    for each in ob:
        res.append(str(each["url"]))
    if not res :
        return None
    else :
        return {"urls":res}


if __name__=="__main__":
    '''this is for testing only'''
    #db.collection.remove()
    db.drop_collection("url_collection")
    ret_of_crawler=[{"url":"www.google.com","appcache":True,"camera":False,"media_queries":True},{"url":"www.yahoo.com","appcache":True,"camera":True,"media_queries":False},{"url":"www.facebook.com","appcache":False,"geotagging":False,"media_queries":True}]

    formattedlist=formatdoc(ret_of_crawler)
    all_fea=["media_queries","geotagging","camera","appcache"]
    print formattedlist
    ''' of the form 
    [{'url': 'www.google.com', 'features': ['media_queries', 'appcache']}, {'url': 'www.yahoo.com', 'features': ['camera', 'appcache']}]
    contains only features which are true for dat website 
    '''
    collection.insert(formattedlist)
    print getfeat(['media_queries'])
