import json
import bottle
from bottle import route, run, request, abort
from core import mon

@route('/restapi/', method='POST')
def getthis():
    url = request.forms.get('url')
    feats = request.forms.get('features')
    if not url and not feats :
       res = None
    elif url and not feats :
       res = mon.geturl(url)
    elif not url and feats :
       if type(feats) == str:
          feats = [feats]
       res = mon.getfeat(feats)
    else :
       res = mon.getres(url,feats)
       
    if not res:
      return {}
    return res
  

run(host='localhost', port=8080)

#Note : need to install bottle to use this
