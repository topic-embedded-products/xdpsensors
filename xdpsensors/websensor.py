from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints
from twisted.application import internet
from twisted.web.server import Site
from twisted.web.static import File
import iio
import iiosensors
import json

motorSpeed_1 = 0
motorSpeed_2 = 0

# class DynamicResource(resource.Resource):
#     #isLeaf = True
#     def __init__(self, uri = None):
#         resource.Resource.__init__(self)
#         self.iio_ctx = iio.Context(uri) # must be kept alive
#         self.xdp_sensors = iiosensors.create_sensor_channel_list(self.iio_ctx, lambda c: c.id.startswith('volt'))
#     def getChild(self, name, request):
#         if name == '':
#             return self
#         return resource.Resource.getChild(self, name, request)
#     def render_GET(self, request):
#         request.setHeader("refresh", "1");
#         request.write('''<html><head><link rel="stylesheet" type="text/css" href="style.css"></head>\n<body><table>''')
#         for s in self.xdp_sensors:
#             request.write("<tr><th>%s</th><td></td><td></td></tr>\n" % s.name.encode('utf-8'))
#             for c in s.channels:
#                 try:
#                     v = c.get()
#                 except OSError as e:
#                     v = e.strerror
#                 request.write("<td></td><td>%s</td><td>%s</td></tr>\n" % (c.name.encode('utf-8'), v))
#         return "</table></body></html>\n"

class DynamicResource(resource.Resource):
    #isLeaf = True
    def __init__(self, uri = None):
        resource.Resource.__init__(self)
        self.iio_ctx = iio.Context(uri) # must be kept alive
        self.xdp_sensors = iiosensors.create_sensor_channel_list(self.iio_ctx, lambda c: c.id.startswith('volt'))
        self.sensorDict = {}
    def get_child(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)
    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


class Bmi088AccelResource(DynamicResource):
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        for accel in self.xdp_sensors:
            accel_name = accel.name.encode('utf-8')
            if accel_name == 'bmi088_accel':
                self.sensorDict[accel_name] = {}
                for channel in accel.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[accel_name][channel_name] = channel_value
        app_json = json.dumps(self.sensorDict)
        return bytes(app_json)


class Bme680Resource(DynamicResource):
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        for bme680 in self.xdp_sensors:
            bme680_name = bme680.name.encode('utf-8')
            if bme680_name == 'bme680':
                self.sensorDict[bme680_name] = {}
                for channel in bme680.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[bme680_name][channel_name] = channel_value
        app_json = json.dumps(self.sensorDict)
        return bytes(app_json)


class Bmi088GyroResource(DynamicResource):
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        for gyro in self.xdp_sensors:
            gyro_name = gyro.name.encode('utf-8')
            if gyro_name == 'bmi088_gyro':
                self.sensorDict = {}
                self.sensorDict[gyro_name] = {}
                for channel in gyro.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[gyro_name][channel_name] = channel_value
                    self.sensorDict[channel_name] = channel_value
        app_json = json.dumps(self.sensorDict)
        return bytes(app_json)

class MotorSpeedResource(DynamicResource):    
    isLeaf = True 
    def render_GET(self, request):
        #print ("TEST 2")
        request.setHeader('Access-Control-Allow-Origin', '*')
        count = 0
        exists = False
        for item in request.args:
            if item == "motorspeed_1":
                exists = True
                break;
            else:
                count += 1
        if exists:
            speedArray = request.args.values()
            motorSpeed_1 = speedArray[count][0]
            print motorSpeed_1
            return "{0}".format(motorSpeed_1) #request.args.values() keys() , values()
        count = 0
        exists = False
        for item in request.args:
            if item == "motorspeed_2":
                exists = True
                break;
            else:
                count += 1
        if exists:
            speedArray = request.args.values()
            motorSpeed_2 = speedArray[count][0]
            print motorSpeed_2
            return "{0}".format(motorSpeed_2) #request.args.values() keys() , values()
        return "-1"
		
class AmsResource(DynamicResource):
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        for ams in self.xdp_sensors:
            ams_name = ams.name.encode('utf-8')
            if ams_name == 'ams':
                self.sensorDict = {}
                self.sensorDict[ams_name] = {}
                for channel in ams.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[ams_name][channel_name] = channel_value
                    self.sensorDict[channel_name] = channel_value
        app_json = json.dumps(self.sensorDict)
        return bytes(app_json)

class CachedFile(static.File):
    def render_GET(self, request):
        request.setHeader("cache-control", "max-age=3600, public")
        return static.File.render_GET(self, request)


def getWebService(uri = None, port = 80, root = '/var/www'):
    root = CachedFile(root)
    root.putChild("dynamic", DynamicResource(uri))
    root.putChild("bmi088_accel", Bmi088AccelResource(uri))
    root.putChild("bme680", Bme680Resource(uri))
    root.putChild("bmi088_gyro", Bmi088GyroResource(uri))
    root.putChild("ams", AmsResource(uri))
    root.putChild("motorspeed", MotorSpeedResource(uri))
    root.putChild("video", File('/media/mmcblk1p3/vid_test.mp4'))
    site = server.Site(root)
    return internet.TCPServer(port, site)

