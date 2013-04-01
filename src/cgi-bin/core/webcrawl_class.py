import sys
import re
import urllib2
import urlparse
import extract_class, mon
import threading

linkregex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>') #regex to find anchor tags leading to other pages

class crawler(threading.Thread) :
    '''crawler class'''
    def __init__(self,url,depth=3):
        threading.Thread.__init__(self)
        self.crawled = set([])
        self.seed = url
        self.webwork = extract_class.website(url,[])
        self.depth = depth
        
    def run(self):
        'crawls the web seed - must be a string, single domain for optimizing stuff in self.webwork'
        tocrawl = set([self.seed])
        for i in range(self.depth) : 
            foundcrawl = set([])
            res = []
            for crawling in tocrawl :
                print "CRAWLING :", crawling
                url = urlparse.urlparse(crawling)
                try:
                    response = urllib2.urlopen(crawling)
                    msg = response.read()
                except:
                    print "could not open %s" % crawling
                    continue
                res.append(self.webwork.process('http://'+url[1]+url[2], msg))
                #form list of res for that iteration and bulk insert later
                links = linkregex.findall(msg) #anchor tags
                self.crawled.add(crawling)
                    
                for link in (links.pop(0) for _ in xrange(len(links))):
                    #print link
                    if link.startswith('/'): #relative
                        link = 'http://' + url[1] + link
                    elif link.startswith('#') or link.startswith("mailto") : #something on the same page
                        pass #link = url.geturl() + url[2] + link
                    elif not link.startswith('http'):
                        link = urlparse.urljoin(url.geturl(),link)
                    if link.find(url[1])!=-1 and link not in self.crawled: #link belong to same domain
                        foundcrawl.add(link)
                        #print link
                #raw_input()
            if res:
                mon.put(res)
            tocrawl = foundcrawl

def process(url,features):
    if not url.startswith("http"):
        url = "http://" + url
    t = crawler(url,1)
    t.start()
    t.join()
    #return mon.findonefun({"url":url},features)

if __name__=='__main__':
    '''for testing only'''
    if len(sys.argv) < 2:
        sys.argv += ["http://snapbird.org/","http://www.ourairports.com/"]
    for each in sys.argv[1:] :
        t = crawler(each) #pass a single url at a time
        t.start()
    '''
    url = raw_input("enter url")
    t = crawler(url)
    t.start()
    t.join()
    '''

#set - no repeat
