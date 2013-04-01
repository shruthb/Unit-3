import cgi, threading
from core import mon, webcrawl_class

print "Content-type: text.html\r\n\r\n"
print ""
print "<html><head><title>"
print "Output</title></head><body>"

form = cgi.FieldStorage()
url = form.getvalue("url")
feats = form.getvalue("feature")
kind = 0
if not url and not feats :
   kind = 1
   res = None
elif url and not feats :
   kind = 2
   res = mon.geturl(url)
elif not url and feats :
   kind = 3
   if type(feats) == str:
      feats = [feats]
      #print feats
   res = mon.getfeat(feats)
else :
   kind = 4
   res = mon.getres(url,feats)

if not res and (kind == 4 or kind == 2):
   print "<h2>We haven't crawled ",url,"yet!</h2>"
   print "<div> Please get back later </div>"
   mon.needtocrawl(url)
   
elif not res and kind == 3:
   print "<h2>We haven't found any url with all these features ",feats,"yet!</h2>"
elif not res and kind == 1:
   print "<h2>What?!</h2>"
else :
   print "<table border='1'>"
   print "<caption><h2>Result of query</h2></caption>"

   for item in res :
      print "<tr><td>%s</td>"%(item)
      if type(res[item]) == list:
         print "<td>"
         for each in res[item]:
            print "%s<br/>"%(each)
         print "</td></tr>"
      else :
         print "<td>%s</td></tr>"%(res[item])
   print "</table>"

print "</body></html>"
