import os
from xdpsensors import websensor
from twisted.application import service

uri = os.environ.get('XDP_URI')
port = os.environ.get('XDP_PORT')
if port:
    port = int(port)
else:
    port = 80
root = os.environ.get('XDP_ROOT') or '/var/www'

application = service.Application("XDP Webserver")
svc = websensor.getWebService(uri, port, root)
svc.setServiceParent(application)
