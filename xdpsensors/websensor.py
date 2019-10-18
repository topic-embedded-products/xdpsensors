from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints
from twisted.application import internet
from twisted.web.server import Site
from twisted.web.static import File
import iio
import iiosensors
import json
import os, time
import subprocess

xdp_last_sample = 0
raptor_last_sample = 0
last_time = time.time();

xdp_last_thr = -1
raptor_last_thr = -1

webcam_curr = "1,0"

hwpath = "/sys/class/hwmon"
hwdirs = os.listdir(hwpath)
motor1_path = ''
motor2_path = ''
motor3_path = ''
motor4_path = ''
for hwdir in hwdirs:
    hwmondir = hwpath + '/' + hwdir
    hwmondirs = os.listdir(hwmondir)
    for hwfile in hwmondirs:
        if (hwfile == 'name'):
            filepath = hwmondir+'/'+hwfile
            namefile = open(filepath, 'r')
            name_str = namefile.readline()
            if name_str[:-1] == "topicmotor": # remove new line    
                motor_dir = hwmondir            
                motor_files = os.listdir(motor_dir)
                for pwm_file in motor_files:
                    print pwm_file
                    if pwm_file == "pwm1":
                        motor1_path = hwmondir+'/'+pwm_file
                        motorSpeed_1 = open(motor1_path, 'r').readline()
                    if pwm_file == "pwm2":
                        motor2_path = hwmondir+'/'+pwm_file
                        motorSpeed_2 = open(motor2_path, 'r').readline()
                    if pwm_file == "pwm3":
                        motor3_path = hwmondir+'/'+pwm_file
                        motorSpeed_3 = open(motor3_path, 'r').readline()
                    if pwm_file == "pwm4":
                        motor4_path = hwmondir+'/'+pwm_file
                        motorSpeed_4 = open(motor4_path, 'r').readline()


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
                self.sensorDict = {}
                #self.sensorDict[accel_name] = {}
                for channel in accel.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[channel_name] = channel_value
                    #self.sensorDict[accel_name][channel_name] = channel_value
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
                self.sensorDict = {}
                #self.sensorDict[bme680_name] = {}
                for channel in bme680.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[channel_name] = channel_value
                    #self.sensorDict[bme680_name][channel_name] = channel_value
        app_json = json.dumps(self.sensorDict)
        return bytes(app_json)
        
        
class Bmm150Resource(DynamicResource):
    def render_GET(self, request):
        request.setHeader("refresh", "1");
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        for bmm150 in self.xdp_sensors:
            bmm150_name = bmm150.name.encode('utf-8')
            if bmm150_name == 'bmm150_magn':
                self.sensorDict = {}
                #self.sensorDict[bmm150_name] = {}
                for channel in bmm150.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    self.sensorDict[channel_name] = channel_value
                    #self.sensorDict[bmm150_name][channel_name] = channel_value
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
                #self.sensorDict[gyro_name] = {}
                for channel in gyro.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    #self.sensorDict[gyro_name][channel_name] = channel_value
                    self.sensorDict[channel_name] = channel_value
        app_json = json.dumps(self.sensorDict)
        return bytes(app_json)
        

class MotorSpeedResource(DynamicResource):   
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
                    f.write(motorSpeed_1)
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
                    f.write(motorSpeed_2)
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
                    f.write(motorSpeed_3)
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
                    f.write(motorSpeed_4)
                    f.close()
                    return "{0}".format(motorSpeed_4)
                else:
                    return "{0}".format(motorSpeed_4)
                break;
            else:
                count += 1
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
                #self.sensorDict[ams_name] = {}
                for channel in ams.channels:
                    channel_name = channel.name.encode('utf-8')
                    try:
                        channel_value = channel.get()
                    except OSError as e:
                        channel_value = e.strerror
                    #self.sensorDict[ams_name][channel_name] = channel_value
                    self.sensorDict[channel_name] = channel_value
        app_json = json.dumps(self.sensorDict)
        return bytes(app_json)
        

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
        raptor_addr = "0xA0002010"
        self.ByteData = {}
        request.setHeader("refresh", "1");
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        diff = curr_time - last_time
        if (diff > 1): # more than a second passed
            xdp_current_sample = int(os.popen("devmem {}".format(xdp_addr)).read(), 0)
            if (xdp_current_sample > xdp_last_sample):
                xdp_throughput = (xdp_current_sample - xdp_last_sample)*bit_data_width
            else:
                xdp_throughput = (0xFFFFFFFF - xdp_last_sample + xdp_current_sample)*bit_data_width
            xdp_last_sample = xdp_current_sample
            raptor_current_sample = int(os.popen("devmem {}".format(raptor_addr)).read(), 0)
            if (raptor_current_sample > raptor_last_sample):
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
        app_json = json.dumps(self.ByteData)
        return bytes(app_json)
        
        
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
            #rerout cam_2 to HDMI
            subprocess.Popen(["dyploroute", "0,0-6,0"])
            if (webcam_curr != "1,0"):
                subprocess.Popen(["dyploroute", "1,0-2,0"])
                webcam_curr = "1,0"
        elif (cam_sel == "cam_2"):
            cam_arg = "1,0"
            #rerout cam_1 to HDMI
            subprocess.Popen(["dyploroute", "0,0-6,0"])
            if (webcam_curr != "0,0"):
                subprocess.Popen(["dyploroute", "0,0-2,0"])
                webcam_curr = "0,0"
        else: # default                    
            cam_arg = "0,0"
            subprocess.Popen(["dyploroute", "1,0-6,0"])
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
            subprocess.Popen(["dyploroute", "4,0-6,0"])
        else:
            if(filter_1 != "none"):
                subprocess.Popen(["dyploroute", "3,0-6,0"])
            else:
                subprocess.Popen(["dyploroute", "{}-6,0".format(cam_arg)])        
        return "-1"
        
class CachedFile(static.File):
    def render_GET(self, request):
        request.setHeader("cache-control", "max-age=3600, public")
        return static.File.render_GET(self, request)


def getWebService(uri = None, port = 9990, root = '/var/www'):
    root = CachedFile(root)
    root.putChild("dynamic", DynamicResource(uri))
    root.putChild("bmi088_accel", Bmi088AccelResource(uri))
    root.putChild("bme680", Bme680Resource(uri))
    root.putChild("bmi088_gyro", Bmi088GyroResource(uri))
    root.putChild("bmm150_magn", Bmm150Resource(uri))
    root.putChild("ams", AmsResource(uri))
    root.putChild("motorspeed", MotorSpeedResource(uri))
    root.putChild("cam_control", CamControlResource())
    root.putChild("throughput", ThroughputResource())
    root.putChild("video", File('/tmp/frame.jpg'))
    site = server.Site(root)
    return internet.TCPServer(port, site)

