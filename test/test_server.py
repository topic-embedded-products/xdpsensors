from twisted.web.server import Site, GzipEncoderFactory
from twisted.web.resource import Resource, EncodingResourceWrapper
from twisted.internet import reactor, endpoints

from twisted.web import server, static
from twisted.internet import reactor, endpoints
from twisted.application import internet
from twisted.web.static import File

import json

motorSpeed = 0

class Bme680Resource(Resource):
    isLeaf = True
    def render_GET(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        with open('bme.json') as f:
            app_json = json.dumps(json.load(f))
        return bytes(app_json)
        
class Bmi088AccelResource(Resource):
    isLeaf = True
    def render_GET(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        with open('bmi_accel.json') as f:
            app_json = json.dumps(json.load(f))
        return bytes(app_json)
        
class Bmi088GyroResource(Resource):
    isLeaf = True    
    def render_GET(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        with open('bmi_gyro.json') as f:
            app_json = json.dumps(json.load(f))
        return bytes(app_json)
        
class AmsResource(Resource):
    isLeaf = True
    def render_GET(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        with open('ams.json') as f:
            app_json = json.dumps(json.load(f))
        return bytes(app_json)
        
class VideoResource(Resource):
    isLeaf = True
    def render_GET(self, request):
        #request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        #with open('ams.json') as f:
        #    app_json = json.dumps(json.load(f))
        return File('vid_test.mp4')
        
class MotorSpeedResource(Resource):
    
    isLeaf = True 
    def render_GET(self, request):
        #print ("TEST 2")
        request.setHeader('Access-Control-Allow-Origin', '*')
        count = 0
        exists = False
        for item in request.args:
            if item == "motorspeed":
                exists = True
                break;
            else:
                count += 1
        if exists:
            speedArray = request.args.values()
            motorSpeed = speedArray[count][0]
            print motorSpeed
        return "{0}".format(motorSpeed) #request.args.values() keys() , values()
        
import cgi

class FormPage(Resource):
    def render_GET(self, request):
        return '<html><body><form method="POST"><input name="the-field" type="text" /></form></body></html>'

    def render_POST(self, request):
        return '<html><body>You submitted: %s</body></html>' % (cgi.escape(request.args["the-field"][0]),)


class CachedFile(static.File):
    def render_GET(self, request):
        request.setHeader("cache-control", "max-age=3600, public")   
        request.setHeader('Access-Control-Allow-Origin', '*')     
        return static.File.render_GET(self, request)
        
root = '/var/www'
#resource = Simple()
root = CachedFile(root)
root.putChild("bmi088_accel", Bmi088AccelResource())
root.putChild("bme680", Bme680Resource())
root.putChild("bmi088_gyro", Bmi088GyroResource())
root.putChild("ams", AmsResource())
root.putChild("video", File('vid_test.mp4'))
root.putChild("motorspeed", MotorSpeedResource())
root.putChild("test", FormPage())

#wrapped = EncodingResourceWrapper(resource, [GzipEncoderFactory()])
site = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 9990)
endpoint.listen(site)
reactor.run()
