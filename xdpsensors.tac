from xdpsensors import websensor
from twisted.application import service

application = service.Application("XDP Webserver")
svc = websensor.getWebService()
svc.setServiceParent(application)
