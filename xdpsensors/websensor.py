from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints
from twisted.application import internet

class DynamicResource(resource.Resource):
    #isLeaf = True
    def __init__(self, uri = None):
        resource.Resource.__init__(self)
        import iio
        import iiosensors
        self.iio_ctx = iio.Context(uri) # must be kept alive
        self.xdp_sensors = iiosensors.create_sensor_channel_list(self.iio_ctx, lambda c: c.id.startswith('volt'))
    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        request.write('''<html><head><link rel="stylesheet" type="text/css" href="style.css"></head>\n<body><table>''')
        for s in self.xdp_sensors:
            request.write("<tr><th>%s</th><td></td><td></td></tr>\n" % s.name.encode('utf-8'))
            for c in s.channels:
                try:
                    v = c.get()
                except OSError as e:
                    v = e.strerror
                request.write("<td></td><td>%s</td><td>%s</td></tr>\n" % (c.name.encode('utf-8'), v))
        return "</table></body></html>\n"

class CachedFile(static.File):
    def render_GET(self, request):
        request.setHeader("cache-control", "max-age=3600, public")
        return static.File.render_GET(self, request)

def getWebService(uri = None, port = 80, root = '/var/www'):
    root = CachedFile(root)
    root.putChild("dynamic", DynamicResource(uri))
    site = server.Site(root)
    return internet.TCPServer(port, site)
