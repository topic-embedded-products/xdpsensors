from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints
from twisted.application import internet
from twisted.web.server import Site
from twisted.web.static import File
import iio
from . import iiosensors
from . import wificonf
import json
import os, time
import subprocess
from serial import Serial

xdp_last_sample = 0
raptor_last_sample = 0
last_time = time.time();
stream = Serial('/dev/ttyPS1', 9600, timeout=3)

xdp_last_thr = -1
raptor_last_thr = -1

webcam_curr = "1,0"

#hwpath = "/sys/class/hwmon"
#hwdirs = os.listdir(hwpath)
motor1_path = '/qdesys/pwm1'
motor2_path = '/qdesys/pwm2'
motor3_path = '/qdesys/pwm3'
motor4_path = '/qdesys/pwm4'


# Keep only one instance of iio.Context alive
class SensorContext:
    def __init__(self, uri = None):
        self.iio_ctx = iio.Context(uri) # must be kept alive
        self.xdp_sensors = iiosensors.create_sensor_channel_list(self.iio_ctx, lambda c: c.id.startswith('volt'))
        self.sensors = {}
        for sensor in self.xdp_sensors:
            self.sensors[sensor.name] = sensor


class DynamicResource(resource.Resource):
    def __init__(self, sensor_context, name):
        resource.Resource.__init__(self)
        self.ctx = sensor_context
        self.sensor = sensor_context.sensors[name]
    def get_child(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)
    def set_default_headers(self):
        self.set_header(b"Access-Control-Allow-Origin", b"*")
        self.set_header(b"Access-Control-Allow-Headers", b"x-requested-with")
        self.set_header(b'Access-Control-Allow-Methods', b'POST, GET, OPTIONS')
    def render_GET(self, request):
        request.setHeader(b"refresh", b"1");
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader(b'Access-Control-Allow-Origin', b'*')
        sensorDict = {}
        for channel in self.sensor.channels:
            try:
                channel_value = channel.get()
            except OSError as e:
                channel_value = e.strerror
            sensorDict[channel.name] = channel_value
        return json.dumps(sensorDict).encode('utf-8')

class MotorSpeedResource(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        global motorSpeed_1
        global motorSpeed_2
        global motorSpeed_3
        global motorSpeed_4
        global motor1_path
        global motor2_path
        global motor3_path
        global motor4_path
        request.setHeader('Access-Control-Allow-Origin', '*')
        count = 0
        for item in request.args:
            if item == "motorSpeed_1":
                speedArray = request.args.values()
                lv_speed = speedArray[count][0]
                if  int(lv_speed) >= 0:
                    motorSpeed_1 = lv_speed
                    f = open(motor1_path,'w')
                    f.write(motorSpeed_1 + "\n")
                    f.close()
                    return "{0}".format(motorSpeed_1)
                else:
                    return "{0}".format(motorSpeed_1)
                break;
            elif item == "motorSpeed_2":
                speedArray = request.args.values()
                lv_speed = speedArray[count][0]
                if  int(lv_speed) >= 0:
                    motorSpeed_2 = lv_speed
                    f = open(motor2_path,'w')
                    f.write(motorSpeed_2 + "\n")
                    f.close()
                    return "{0}".format(motorSpeed_2)
                else:
                    return "{0}".format(motorSpeed_2)
                break;
            elif item == "motorSpeed_3":
                speedArray = request.args.values()
                lv_speed = speedArray[count][0]
                if  int(lv_speed) >= 0:
                    motorSpeed_3 = lv_speed
                    f = open(motor3_path,'w')
                    f.write(motorSpeed_3 + "\n")
                    f.close()
                    return "{0}".format(motorSpeed_3)
                else:
                    return "{0}".format(motorSpeed_3)
                break;
            elif item == "motorSpeed_4":
                speedArray = request.args.values()
                lv_speed = speedArray[count][0]
                if  int(lv_speed) >= 0:
                    motorSpeed_4 = lv_speed
                    f = open(motor4_path,'w')
                    f.write(motorSpeed_4 + "\n")
                    f.close()
                    return "{0}".format(motorSpeed_4)
                else:
                    return "{0}".format(motorSpeed_4)
                break;
            else:
                count += 1
        return "-1"

def print_longitude(longitude, amount_first_degrees):
    return longitude[0:amount_first_degrees].strip("0") + "." + longitude[amount_first_degrees:amount_first_degrees+2]

def parse_gps_message(message):
    output = message.split(',')
    if len(output) < 8:
        return "Problem with GPS message"
    if output[6] == "0":
        return " has no fix"
    return "fix with {} satellites. Lat: {}, Long: {}".format(output[7], print_longitude(output[2], 2), print_longitude(output[4], 3))

def fetch_gps():
    count = 0
    while(count < 10):
        readback = stream.read_until()
        value = readback.decode('ascii', errors='ignore')
        if 'GNGGA' in value or 'GPGGA' in value:
            return parse_gps_message(value)
        count = count + 1
    return "Could not retrieve GPS information"

class ThroughputResource(resource.Resource):
    def render_GET(self, request):
        global xdp_last_sample
        global raptor_last_sample
        global last_time
        global xdp_last_thr
        global raptor_last_thr
        curr_time = time.time()
        bit_data_width = 256
        scale = 8*1024*1024 # MB
        xdp_addr = "0xA0002000"
        raptor_addr = "0xA0002008"
        self.ByteData = {}
        request.setHeader("refresh", "1");
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        diff = curr_time - last_time
        if (diff > 1): # more than a second passed
            xdp_current_sample = int(os.popen("devmem {}".format(xdp_addr)).read(), 0)
            if (xdp_current_sample >= xdp_last_sample):
                xdp_throughput = (xdp_current_sample - xdp_last_sample)*bit_data_width
            else:
                xdp_throughput = (0xFFFFFFFF - xdp_last_sample + xdp_current_sample)*bit_data_width
            xdp_last_sample = xdp_current_sample
            raptor_current_sample = int(os.popen("devmem {}".format(raptor_addr)).read(), 0)
            if (raptor_current_sample >= raptor_last_sample):
                raptor_throughput = (raptor_current_sample - raptor_last_sample)*bit_data_width
            else:
                raptor_throughput = (0xFFFFFFFF - raptor_last_sample + raptor_current_sample)*bit_data_width
            raptor_last_sample = raptor_current_sample
            xdp_last_thr = int((xdp_throughput / scale) / diff)
            raptor_last_thr = int((raptor_throughput / scale) / diff)
            last_time = curr_time;
        self.ByteData["XDP"] = xdp_last_thr
        self.ByteData["Raptor"] = raptor_last_thr
        self.ByteData["Time"] = diff
        self.ByteData["gps"] = fetch_gps()
        app_json = json.dumps(self.ByteData)
        return app_json.encode('utf-8')


class CamControlResource(resource.Resource):
    def render_GET(self, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        count = 0
        data = request.args.values()
        global webcam_curr

        for item in request.args:
            if item == "cam_sel":
                cam_sel = data[count][0]
            if item == "filter_1":
                filter_1 = data[count][0]
            if item == "filter_2":
                filter_2 = data[count][0]
            count = count +1

        if (cam_sel == "cam_1"):
            cam_arg = "0,0"
            #rerout cam_1 to HDMI
            subprocess.Popen(["dyploroute", "0,0-0,0"])
            if (webcam_curr != "1,0"):
                #rerout cam_2 to WebCam
                subprocess.Popen(["dyploroute", "1,0-2,0"])
                webcam_curr = "1,0"
        elif (cam_sel == "cam_2"):
            cam_arg = "1,0"
            #rerout cam_2 to HDMI
            subprocess.Popen(["dyploroute", "1,0-0,0"])
            if (webcam_curr != "0,0"):
                #rerout cam_1 to WebCam
                subprocess.Popen(["dyploroute", "0,0-2,0"])
                webcam_curr = "0,0"
        else: # default
            cam_arg = "0,0"
            subprocess.Popen(["dyploroute", "1,0-0,0"])
            if (webcam_curr != "1,0"):
                subprocess.Popen(["dyploroute", "1,0-2,0"])
                webcam_curr = "1,0"

        if (filter_1 != "none"):
            subprocess.Popen(["dyploroute", "{}-3,0".format(cam_arg)])
            if (filter_1 == "Contrast"):
                filter1_arg = "rgb_contrast"
            elif (filter_1 == "Grayscale"):
                filter1_arg = "rgb_grayscale"
            elif (filter_1 == "Threshold"):
                filter1_arg = "rgb_threshold"
            else:
                filter1_arg = "rgb_grayscale"
            subprocess.Popen(["dyploprogrammer", "{}".format(filter1_arg), "3"])

        if (filter_2 != "none"):
            if(filter_1 != "none"):
                subprocess.Popen(["dyploroute", "3,0-4,0"])
            else:
                subprocess.Popen(["dyploroute", "{}-4,0".format(cam_arg)])
            if (filter_2 == "Contrast"):
                filter2_arg = "rgb_contrast"
            elif (filter_2 == "Grayscale"):
                filter2_arg = "rgb_grayscale"
            elif (filter_2 == "Threshold"):
                filter2_arg = "rgb_threshold"
            else:
                filter2_arg = "rgb_grayscale"
            subprocess.Popen(["dyploprogrammer", "{}".format(filter2_arg), "4"])
            subprocess.Popen(["dyploroute", "4,0-0,0"])
        else:
            if(filter_1 != "none"):
                subprocess.Popen(["dyploroute", "3,0-0,0"])
            else:
                subprocess.Popen(["dyploroute", "{}-0,0".format(cam_arg)])
        return "-1"

class CachedFile(static.File):
    def render_GET(self, request):
        request.setHeader(b"cache-control", b"max-age=3600, public")
        return static.File.render_GET(self, request)

# Make sure /tmp/frame.jpg' exists, otherwise the web page will look horrible
def create_frame_file():
    if os.path.exists('/tmp/frame.jpg'):
        return
    try:
        import shutil
        shutil.copyfile('/var/www/camera.jpg', '/tmp/frame.jpg')
    except:
        pass

def getWebService(uri = None, port = 80, root = '/var/www'):
    create_frame_file()
    root = CachedFile(root)
    ctx = SensorContext(uri)
    for s in (ctx.sensors.keys()):
        root.putChild(s.encode('utf-8'), DynamicResource(ctx, s))
    root.putChild(b"motorspeed", MotorSpeedResource())
    root.putChild(b"cam_control", CamControlResource())
    root.putChild(b"throughput", ThroughputResource())
    root.putChild(b"video", File(b'/tmp/frame.jpg'))
    root.putChild(b"wifi", wificonf.WifiResource())
    site = server.Site(root)
    return internet.TCPServer(port, site)
