import re
import urllib2, urlparse

class website(): #threading.Thread

    def __init__(self,baseurl,features):
        self.url = baseurl
        self.features = features
        self.domCss = {} # dict of external css sheets for page, string : tuple of attr
        self.domScripts = {} # key = script url, val = content of script url

    def getContent(self,relurl):
        "gets script/style content from link tag's href or @import's url()"
        if relurl.startswith('/'):
            link =  self.url+ relurl
        elif relurl.startswith("http"):
            link = relurl
        else: #not sure - error was because of href="domain.css" which is relative but doesn't start with /
            link = urlparse.urljoin(self.cururl,relurl)
        try :
            #print link
            resp = urllib2.urlopen(link)
            content = resp.read()
            return content
        except : 
            print "Couldn't open link"
            return ''
    
    #findall - list of groups=strings

    def atMedia(self,cssContent):
        "searches for @media rules in css content"
        #mediaType = "((only |not )?(?P<mediaType>braille|embossed|handheld|print|projection|screen|speech|tty|tv|all) (and|,))*?" #
        mediaFeature = re.compile("width|height|device-width|device-height|orientation|aspect-ratio|device-aspect-ratio|color|color-index|monochrome|resolution|scan|grid")
        mediaAtRule = re.compile("@media\s(?P<mediaQuery>.*?){[^}]*?}") #@media rule within style tag or imported doc
        count = 0 #len(mediaAtRule.findall(cssContent))
        for meq in mediaAtRule.finditer(cssContent) :
            if mediaFeature.search(meq.group(1)):
                count += 1
        return count


    def get_external_css(self,page): #,css
        "get css which is specified using link tag and check it for media queries"
        #print "External css : "
        extStylesRe = re.compile("<link (.*?href=['\"](.*?\.css).*?['\"].*?)\s?/>")  #link to external style sheet
        #mediaType = "((only |not )?(?P<mediaType>braille|embossed|handheld|print|projection|screen|speech|tty|tv|all) (and|,))*?"
        mediaFeature = re.compile("width|height|device-width|device-height|orientation|aspect-ratio|device-aspect-ratio|color|color-index|monochrome|resolution|scan|grid")
        mediaAttrRe = re.compile("media=['\"](?P<mediaFeature>.*?)['\"]") #media type - link's attr
        mediaAtRule = re.compile("@media (?P<media>[^{]*?){[^}]*?}") #@media rule in .css file 
        mediaCount = 0
        for each in extStylesRe.findall(page):
            #print each
            meq = mediaAttrRe.search(each[0])
            if each[1] in self.domCss.keys():
                mediaCount += self.domCss[each[1]][1];
            elif meq and mediaFeature.search(meq.group(1)):
                #print "media"
                mediaCount += 1
                self.domCss[each[1]] = ['',1]
            else : #not extracting if media="" was already in link tag
                cssContent = self.getContent(each[1])
                #css.append(cssContent)
                count = self.atMedia(cssContent)
                mediaCount += count
                self.domCss[each[1]] = (cssContent,count) #or []
                #print "css content : \n",cssContent
        return mediaCount


    def get_import_media(self,cssContent):
        "get css which is specified using @import rule and check it for media queries"
        importAtRe = re.compile("@import url\(['\"](.*?\.css).*?['\"]\)(?P<media>.*?);") #@import rule within style tag with media spec
        mediaFeature = re.compile("width|height|device-width|device-height|orientation|aspect-ratio|device-aspect-ratio|color|color-index|monochrome|resolution|scan|grid")
        mediaCount = 0
        for each in importAtRe.findall(cssContent):
            if each[0] in self.domCss.keys():
                mediaCount += self.domCss[each[1]][1]
            elif each[1] and mediaFeature.search(each[1]):
                mediaCount += 1
                self.domCss[each[1]] = ('',1)
            else:
                cssContent = self.getContent(each[0])
                #css.append(cssContent)
                count = self.atMedia(cssContent)
                mediaCount += count
                self.domCss[each[0]] = (cssContent,count) #or []
                #print "css content : \n",cssContent
        return mediaCount


    def get_internal_css(self,page):
        "get css which is written within style tag and check it for media queries"
        intStyleRe = re.compile("<style type=['\"]text/css['\"]>(.*?)</style>") #internal style tag
        #mediaAtRule = re.compile("@media (?P<media>[^{]*?){[^}]*?}") #@media rule within style tag or imported doc
        
        style = intStyleRe.findall(page)
        mediaCount = 0
        #print "internal css / css page : "
        for each in style :
            mediaCount += self.atMedia(each)    
            mediaCount += self.get_import_media(each)
        return mediaCount


    def mediaQueries(self,page):
        "check the page for media queries"
        #css = []
        count = self.get_external_css(page) #,css)
        count += self.get_internal_css(page) #,css)
        #count += atMedia(css)
        if count>1 :
            return True
        else:
            return False
        
    def camera(self,page,script):
        "check if the capture attribute is used for media capture"
        getmedRe = re.compile("navigator\.[a-z]*?[gG]etUserMedia\(");
        captre = re.compile("<input .*? capture.*?/?>")
        for each in script :
            if getmedRe.search(each) :
                return True
        if captre.search(page):
            return True
        else:
            return False

    #\s?(?P<lang>type=\"text/javascript\")?

    def getscript(self,page):
        "get script from page - script tag content and external src"
        common = ["http://ajax.googleapis.com/ajax/libs/jquery/1.8/jquery.min.js"]
        scriptre = re.compile("<script.*?>(.+?)</script>",re.DOTALL)
        scripts = scriptre.findall(page)
        scriptlinksre = re.compile("<script .*?src=['\"](.*?\.js.*?)['\"].*?></script>")
        scriptlinks = scriptlinksre.findall(page)
        #print "scriptlinks : ",scriptlinks
        for each in scriptlinks :
            if each not in common :
                if each in self.domScripts.keys() :
                    scripts.append(self.domScripts[each])
                else :
                    scriptContent = self.getContent(each)
                    scripts.append(scriptContent)
                    self.domScripts[each] = scriptContent
        #print len(scriptlinks) #scripts,'\n',
        return scripts

    def localstorage(self,script):
        "check if the localStorage api is used by the page"
        locstore = re.compile("(window\.)?localStorage.?")
        for each in script :
            if locstore.search(each) :
                return True
        return False

    def geolocation(self,script):
        "check if the geolocation api is used by the page"
        geore = re.compile("(window\.)?navigator.geolocation")
        for each in script :
            if geore.search(each) :
                return True
        return False

    def touch(self,page,script):
        "check if the touch event is used by the page"
        touchre = re.compile("(\.addEventListener\([\"']touch(start|move|end|cancel)[\"'])|(\.ontouch(start|move|end|cancel)=)")
        touchpagere = re.compile("<.*? ontouch(start|move|end|cancel)=\".*?\" .*?>")
        if touchpagere.search(page) :
            return True
        for each in script :
            if touchre.search(each) :
                return True
        return False
        
    def process(self, url ,page): #url here = baseurl + path
        "process url for the various features"
        self.cururl = url
        m = self.mediaQueries(page)
        script = self.getscript(page)
        g = self.geolocation(script)
        l = self.localstorage(script)
        c = self.camera(page,script)
        t = self.touch(page,script)
        return {"url":url,"media queries":m,"geolocation":g,"local storage":l,"camera":c,"touch":t}

    
if __name__=='__main__':
    '''this is for testing this module'''
    crurl = "http://maps.google.com"
    w = website(crurl,[])
    try :
        doc = urllib2.urlopen(crurl) #crawling
        content = doc.read()
    except : 
        print "could not read",crurl
    #print content[:100]
    res = w.process(crurl,content)
    for each in res:
        print each, res[each]
