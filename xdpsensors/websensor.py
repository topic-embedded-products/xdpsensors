from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints
from twisted.application import internet
import iio
import iiosensors

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
        return self.sensorDict


class Bme680Resource(DynamicResource):
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        # self.setHeader('Access-Control-Allow-Origin', '*')
        # self.setHeader('Access-Control-Allow-Methods', 'GET')
        # self.setHeader('Access-Control-Allow-Headers',
        #                'x-prototype-version,x-requested-with')
        # self.setHeader('Access-Control-Max-Age', 2520)
        # self.setHeader('Content-type', 'application/json')
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
        return self.sensorDict


class Bmi088GyroResource(DynamicResource):
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        for gyro in self.xdp_sensors:
            gyro_name = gyro.name.encode('utf-8')
            if gyro_name == 'bmi088_gyro':
                self.sensorDict[gyro_name] = {}
                for channel in gyro.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[gyro_name][channel_name] = channel_value
        return self.sensorDict


class AmsResource(DynamicResource):
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        for ams in self.xdp_sensors:
            ams_name = ams.name.encode('utf-8')
            if ams_name == 'ams':
                self.sensorDict[ams_name] = {}
                for channel in ams.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[ams_name][channel_name] = channel_value
        return self.sensorDict


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
    site = server.Site(root)
    return internet.TCPServer(port, site)

