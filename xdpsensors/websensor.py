from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints
from twisted.application import service, internet

class RootResource(resource.Resource):
    isLeaf = True
    def __init__(self):
        resource.Resource.__init__(self)
        import iio
        import iiosensors
        self.iio_ctx = iio.Context() # must be kept alive
        self.xdp_sensors = iiosensors.create_sensor_channel_list(iio_ctx, lambda c: c.id.startswith('volt'))
    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)
    def render_GET(self, request):
        if not request.postpath[0]:
            request.setHeader("refresh", "1");
        request.write("<html><body>\n<table>\n")
        for s in self.xdp_sensors:
            request.write("<tr><td>%s</td><td></td><td></td></tr>\n" % s.name.encode('utf-8'))
            for c in s.channels:
                try:
                    v = c.get()
                except OSError as e:
                    v = e.strerror
                request.write("<td></td><td>%s</td><td>%s</td></tr>\n" % (c.name.encode('utf-8'), v))
        return "</table>\n</body></html>\n"

def getWebService():
    root = RootResource()
    site = server.Site(root)
    root.putChild("favicon.ico", static.File("/var/www/favicon.ico"))
    return internet.TCPServer(80, site)

application = service.Application("XDP Webserver")
service = getWebService()
service.setServiceParent(application)
