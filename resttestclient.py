import json
import urlparse
import urllib2
import urllib

headers = {'Accept': 'application/json','Content-Type': 'application/json; charset=UTF-8'}
url = 'http://localhost:8080/restapi/'
data = {"url":"http://www.yahoo.com"}

request = urllib2.Request(url)
request.add_data(urllib.urlencode(data))
for key,value in headers.items() :
  request.add_header(key,value)

response = urllib2.urlopen(request)

#print response.info().headers
resdata =  response.read() #json reply
jsonres = json.loads(resdata) # parse content with the json module
#print jsonres
for each in jsonres:
  print each,':', jsonres[each]

# This is a sample rest client for the rest interface provided
