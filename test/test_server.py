from twisted.web.server import Site, GzipEncoderFactory
from twisted.web.resource import Resource, EncodingResourceWrapper
from twisted.internet import reactor, endpoints

from twisted.web import server, static
from twisted.internet import reactor, endpoints
from twisted.application import internet
from twisted.web.static import File

import json

motorSpeed_1 = 0
motorSpeed_2 = 0
motorSpeed_3 = 0
motorSpeed_4 = 0

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
            if item == "motorSpeed_1":
                speedArray = request.args.values()
                motorSpeed_1 = speedArray[count][0]
                print ("Motor 1 speed set: "+str(motorSpeed_1))
                return "{0}".format(motorSpeed_1)
                break;
            elif item == "motorSpeed_2":
                speedArray = request.args.values()
                motorSpeed_2 = speedArray[count][0]
                print ("Motor 2 speed set: "+str(motorSpeed_2))
                return "{0}".format(motorSpeed_2)
                break;
            elif item == "motorSpeed_3":
                speedArray = request.args.values()
                motorSpeed_3 = speedArray[count][0]
                print ("Motor 3 speed set: "+str(motorSpeed_3))
                return "{0}".format(motorSpeed_3)
                break;
            elif item == "motorSpeed_4":
                speedArray = request.args.values()
                motorSpeed_4 = speedArray[count][0]
                print ("Motor 4 speed set: "+str(motorSpeed_4))
                return "{0}".format(motorSpeed_4)
                break;
            else:
                count += 1
        return "-1"
        
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
root.putChild("test_index", File('drone-frontend/index.html'))
root.putChild("motorspeed", MotorSpeedResource())
root.putChild("test", FormPage())

#wrapped = EncodingResourceWrapper(resource, [GzipEncoderFactory()])
site = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 9990)
endpoint.listen(site)
reactor.run()
